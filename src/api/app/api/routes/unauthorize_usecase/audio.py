from __future__ import annotations



import logging



from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile



from app.core.session_language import resolve_stt_language

from app.models.audio.tts_request import TtsRequest

from app.services.ai.audio_handler_service import text_to_speech, transcribe_audio



logger = logging.getLogger(__name__)



router = APIRouter(tags=["audio"])





@router.post(

    "/audio/speech-to-text",

    summary="Speech-to-text (UC-12, Hugging Face local hoặc Whisper)",

    description="Multipart: `session_id` + `file` audio (webm/wav, max 25MB). Tùy chọn `language` (BCP-47, ví dụ `vi`) khi session chưa có ngôn ngữ từ chat. STT: `HF_SPEECH_MODEL_ID` (mặc định Gemma-4) tải vào thư mục gốc project `models/...` hoặc fallback `OPENAI_STT_DEPLOYMENT`. Returns `{ \"text\": \"...\" }`.",

)

async def speech_to_text(

    session_id: str = Form(..., description="Chat session UUID"),

    file: UploadFile = File(..., description="Audio recording"),

    language: str | None = Form(

        None,

        description="BCP-47 (vi, en, …). Dùng khi chưa có ngôn ngữ từ chat; mặc định server: DEFAULT_STT_LANGUAGE.",

    ),

) -> dict[str, str]:

    if not session_id.strip():

        raise HTTPException(status_code=400, detail="session_id is required")

    data = await file.read()

    lang = resolve_stt_language(session_id.strip(), language)

    try:

        text = await transcribe_audio(

            filename=file.filename or "audio.webm",

            content_type=file.content_type,

            data=data,

            session_language=lang,

        )

    except ValueError as exc:

        if str(exc) == "empty_transcription":

            raise HTTPException(

                status_code=422,

                detail=(

                    "Không nhận diện được giọng nói. Vui lòng thử lại hoặc nhập bằng bàn phím."

                    if (lang or "").lower().startswith("vi")

                    else "Could not recognize speech. Please try again or type your message."

                ),

            ) from exc

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except RuntimeError as exc:

        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except Exception:

        logger.exception("speech-to-text failed")

        raise HTTPException(

            status_code=502,

            detail="Speech service error. Please try again later.",

        ) from None

    return {"text": text}





@router.post(

    "/audio/text-to-speech",

    summary="Text-to-speech (edge-tts, mp3)",

    description="JSON: `text`, `voice`, `response_format`. Tổng hợp giọng qua edge-tts (mp3); `SPEECH_TTS_EDGE_VOICE` (hoặc `TTS_LOCAL_VOICE`) chọn giọng. Mô hình HF được dùng cho STT, không cho TTS.",

    response_class=Response,

)

async def tts_endpoint(payload: TtsRequest) -> Response:

    try:

        audio_bytes, media_type = await text_to_speech(

            text=payload.text,

            voice=payload.voice,

            response_format=payload.response_format,

        )

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except RuntimeError as exc:

        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except Exception:

        logger.exception("text-to-speech failed")

        raise HTTPException(

            status_code=502,

            detail="TTS service error. Please try again later.",

        ) from None

    return Response(content=audio_bytes, media_type=media_type)

