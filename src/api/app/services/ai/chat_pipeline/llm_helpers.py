from __future__ import annotations

import json
from typing import Any

from app.core.utilities.safe_dict import SafeDict
from app.core.config import get_settings
from app.core.session_store import get_session_store
from app.services.ai.azure_client import get_async_openai_client
from app.services.general.patient_validators import (
    FIELD_VALIDATORS,
    normalize_date_of_birth,
    normalize_phone,
)
from app.core.enumerations.languages_enum import Languages

TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "update_patient_draft",
        "description": "Save or update known patient fields from the user message. "
        "Omit a field if not mentioned.",
        "parameters": {
            "type": "object",
            "properties": {
                "full_name": {"type": "string"},
                "date_of_birth": {"type": "string", "description": "dd/mm/yyyy or yyyy-mm-dd"},
                "gender": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "address": {"type": "string"},
            },
        },
    },
}


def _normalize_gender(raw: str) -> str:
    m = raw.strip().lower()
    if m in ("nam", "male", "m"):
        return "MALE"
    if m in ("nữ", "nu", "female", "f"):
        return "FEMALE"
    return "OTHER"


async def chat_json(system: str, user: str) -> dict[str, Any]:
    client = get_async_openai_client()
    settings = get_settings()
    response = await client.chat.completions.create(
        model=settings.openai_deployment,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    raw = (response.choices[0].message.content or "").strip()
    return json.loads(raw)


async def classify_medical(user_message: str, language: Languages = "vi") -> int:
    system_dict: SafeDict[Languages, str] = SafeDict({
        "en": ("You output JSON only: {\"relevance_score\": 0-100} measuring how the message "
            "is about health, symptoms, medical advice, or booking care. 100 = fully medical, "
            "0 = not medical (weather, code, games, etc.)."),
        "vi": ("Bạn xuất JSON chỉ: {\"relevance_score\": 0-100} đo lường mức độ liên quan của tin nhắn "
            "đến sức khỏe, triệu chứng, lời khuyên y tế, hoặc đặt lịch khám. 100 = hoàn toàn y tế, "
            "0 = không liên quan (thời tiết, mã, trò chơi, v.v.)."),
        "jp": ("あなたはJSONのみを出力します：{\"relevance_score\": 0-100} メッセージが健康、症状、医療アドバイス、または予約されたケアに関連しているかどうかを測定します。"
            "100 = 完全に医療、0 = 非医療（天気、コード、ゲームなど）。"),
    }, fallback_key="en")
    system = system_dict[language]
    
    data = await chat_json(system, user_message)
    score = data.get("relevance_score", 0)
    return int(score) if isinstance(score, (int, float)) else 0


async def triage_department(
    departments: list[dict[str, Any]], user_context: str
) -> dict[str, Any]:
    depts = json.dumps(
        [
            {"id": d["id"], "name": d["name"], "description": d.get("description")}
            for d in departments
        ],
        ensure_ascii=False,
    )
    system = (
        "You help route the patient to ONE department. Output JSON only:\n"
        '{ "department_id": number | null, "need_clarification": boolean, "short_question": string | null }\n'
        "Rules: Pick department_id from the list if confident. If not enough information, "
        "set need_clarification true and one short follow-up in short_question. "
        "Do not use department_id not in the list.\n"
        f"Departments: {depts}\n"
    )
    return await chat_json(system, user_context)


async def triage_department_from_shortlist(
    shortlist: list[dict[str, Any]], user_context: str
) -> dict[str, Any]:
    short = json.dumps(
        [
            {
                "id": d["department_id"],
                "name": d["name"],
                "description": d.get("description"),
                "symptoms_keywords": d.get("symptoms_keywords"),
            }
            for d in shortlist
        ],
        ensure_ascii=False,
    )
    ids = ", ".join(str(d["department_id"]) for d in shortlist)
    system = (
        "You route to exactly one department from a shortlist only. Output JSON only:\n"
        '{ "department_id": number | null, "need_clarification": boolean, "short_question": string | null }\n'
        "Rules: department_id MUST be one of the allowed IDs or null if uncertain. "
        "If uncertain, set need_clarification true and provide one concise question.\n"
        f"Allowed department IDs: [{ids}]\n"
        f"Shortlist: {short}\n"
    )
    return await chat_json(system, user_context)


async def classify_booking(user_message: str) -> dict[str, Any]:
    system = (
        "Output JSON only: {\"agreement_score\": 0-100, \"intent\": \"yes\"|\"no\"|\"unclear\"} "
        "for whether the user wants to pre-book a hospital visit. High score = clear yes, low = clear no."
    )
    return await chat_json(system, user_message)


def _apply_tool_args(info: dict[str, Any], args: dict[str, Any], *, lang: str) -> None:
    for key, raw in args.items():
        if key not in FIELD_VALIDATORS or raw is None:
            continue
        if isinstance(raw, str) and not raw.strip():
            continue
        val: Any = raw
        if key == "phone" and isinstance(raw, str):
            val = normalize_phone(raw)
        if key == "date_of_birth" and isinstance(raw, str):
            val = normalize_date_of_birth(raw)
        if key == "gender" and isinstance(raw, str):
            val = _normalize_gender(str(raw))
        ok, _ = FIELD_VALIDATORS[key](val, lang)
        if ok:
            info[key] = val


def _append_assistant_tool_msg(msgs: list[dict[str, Any]], message: Any) -> None:
    out: dict[str, Any] = {
        "role": "assistant",
        "content": message.content or "",
    }
    if message.tool_calls:
        out["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in message.tool_calls
        ]
    msgs.append(out)


async def run_pii_pass(session_id: str, user_message: str, state: Any) -> str:
    client = get_async_openai_client()
    settings = get_settings()
    store = get_session_store()
    history = store.get_history(session_id)
    known = json.dumps(state.patient_info, ensure_ascii=False)
    system = (
        "You are a medical reception assistant. The user is providing registration data. "
        "You MUST call the function `update_patient_draft` with any fields the user just gave. "
        "Required: full name, date of birth, gender, phone. Optional: email, address. "
        f"Current draft: {known}\n"
        "Be brief. After calling tools, reply in one short friendly sentence: "
        "either ask for the next missing required field or confirm you have everything."
    )
    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for m in history[-12:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_message})

    lang = "vi"
    for _ in range(4):
        response = await client.chat.completions.create(
            model=settings.openai_deployment,
            messages=messages,
            tools=[TOOL_DEF],
            tool_choice="auto",
            temperature=0.3,
        )
        choice = response.choices[0].message
        if choice.tool_calls:
            _append_assistant_tool_msg(messages, choice)
            for tc in choice.tool_calls:
                if tc.function.name == "update_patient_draft":
                    try:
                        args = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    if isinstance(args, dict):
                        _apply_tool_args(state.patient_info, args, lang=lang)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(
                            {"ok": True, "draft": state.patient_info},
                            ensure_ascii=False,
                        ),
                    }
                )
            continue
        return (choice.content or "").strip()
    return "Please provide your full name, date of birth, gender, and 10-digit phone number."
