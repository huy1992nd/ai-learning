"""UC-05 field validation (FR-05-02). Messages are returned in the requested language code."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def _msg(lang: str, vi: str, en: str) -> str:
    return vi if (lang or "").lower().startswith("vi") else en


def validate_full_name(value: Any, lang: str) -> tuple[bool, str | None]:
    if not isinstance(value, str):
        return False, _msg(lang, "Họ tên không hợp lệ.", "Full name is invalid.")
    s = " ".join(value.split())
    if len(s) < 3:
        return False, _msg(lang, "Họ tên quá ngắn.", "Full name is too short.")
    if len(s.split()) < 2:
        return False, _msg(
            lang,
            "Vui lòng nhập họ và tên đầy đủ (ít nhất 2 từ).",
            "Please enter at least two words (given name and family name).",
        )
    return True, None


def validate_date_of_birth(value: Any, lang: str) -> tuple[bool, str | None]:
    if not isinstance(value, str):
        return False, _msg(lang, "Ngày sinh không hợp lệ.", "Date of birth is invalid.")
    s = value.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s, fmt).date()
            break
        except ValueError:
            d = None
    else:
        return False, _msg(
            lang,
            "Ngày sinh phải theo dạng dd/mm/yyyy.",
            "Date of birth must be dd/mm/yyyy.",
        )
    if d > date.today():
        return False, _msg(lang, "Ngày sinh không được là tương lai.", "Date of birth cannot be in the future.")
    return True, None


def normalize_date_of_birth(value: str) -> str:
    """Store as dd/mm/yyyy for display consistency."""
    s = value.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s, fmt).date()
            return d.strftime("%d/%m/%Y")
        except ValueError:
            continue
    return s


def validate_gender(value: Any, lang: str) -> tuple[bool, str | None]:
    if not isinstance(value, str):
        return False, _msg(lang, "Giới tính không hợp lệ.", "Gender is invalid.")
    g = value.strip().lower()
    allowed = {
        "male",
        "female",
        "other",
        "nam",
        "nữ",
        "nu",
        "khác",
        "khac",
        "m",
        "f",
    }
    if g not in allowed and len(g) < 1:
        return False, _msg(lang, "Vui lòng chọn giới tính.", "Please specify gender.")
    return True, None


def validate_phone(value: Any, lang: str) -> tuple[bool, str | None]:
    if not isinstance(value, str):
        return False, _msg(lang, "Số điện thoại không hợp lệ.", "Phone number is invalid.")
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("84"):
        digits = "0" + digits[2:]
    if len(digits) != 10 or not digits.startswith("0"):
        return False, _msg(
            lang,
            "Số điện thoại phải có 10 chữ số và bắt đầu bằng 0.",
            "Phone must be 10 digits starting with 0.",
        )
    return True, None


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("84"):
        digits = "0" + digits[2:]
    return digits


def validate_email(value: Any, lang: str) -> tuple[bool, str | None]:
    if value is None or value == "":
        return True, None
    if not isinstance(value, str):
        return False, _msg(lang, "Email không hợp lệ.", "Email is invalid.")
    if not _EMAIL_RE.match(value.strip()):
        return False, _msg(lang, "Định dạng email không đúng.", "Email format is invalid.")
    return True, None


def validate_citizen_identity_number(value: Any, lang: str) -> tuple[bool, str | None]:
    if value is None or value == "":
        return True, None
    if not isinstance(value, str):
        return False, _msg(lang, "Số CCCD không hợp lệ.", "ID number is invalid.")
    digits = re.sub(r"\D", "", value)
    if len(digits) != 12:
        return False, _msg(lang, "CCCD phải gồm 12 chữ số.", "National ID must be 12 digits.")
    return True, None


def validate_health_insurance_number(value: Any, lang: str) -> tuple[bool, str | None]:
    if value is None or value == "":
        return True, None
    if not isinstance(value, str):
        return False, _msg(lang, "Mã BHYT không hợp lệ.", "Insurance id is invalid.")
    alnum = re.sub(r"[^0-9A-Za-z]", "", value)
    if len(alnum) < 10:
        return False, _msg(lang, "Mã BHYT không hợp lệ.", "Insurance id is invalid.")
    return True, None


def validate_address(value: Any, lang: str) -> tuple[bool, str | None]:
    if not isinstance(value, str):
        return False, _msg(lang, "Địa chỉ không hợp lệ.", "Address is invalid.")
    s = value.strip()
    if len(s) < 5:
        return False, _msg(lang, "Địa chỉ quá ngắn.", "Address is too short.")
    return True, None


FIELD_VALIDATORS = {
    "full_name": validate_full_name,
    "date_of_birth": validate_date_of_birth,
    "gender": validate_gender,
    "phone": validate_phone,
    "email": validate_email,
    "citizen_identity_number": validate_citizen_identity_number,
    "health_insurance_number": validate_health_insurance_number,
    "address": validate_address,
}

# Minimal PII to open registration (address optional; used by healthcare v2)
REQUIRED_PII_DRAFT = ("full_name", "date_of_birth", "gender", "phone")


def pii_draft_minimal_complete(info: dict[str, Any]) -> bool:
    for k in REQUIRED_PII_DRAFT:
        v = info.get(k)
        if v is None or (isinstance(v, str) and not v.strip()):
            return False
    return True
