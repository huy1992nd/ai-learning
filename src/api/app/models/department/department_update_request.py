from __future__ import annotations

from pydantic import BaseModel, field_validator, model_validator

from app.models.department._validators import _normalize_optional_str


class DepartmentUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    specialty: str | None = None
    symptoms_keywords: str | None = None
    common_diseases: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: object | None) -> str | None:
        if v is None:
            return None
        return str(v).strip()

    @field_validator(
        "description",
        "specialty",
        "symptoms_keywords",
        "common_diseases",
        mode="before",
    )
    @classmethod
    def normalize_optionals(cls, v: object | None) -> str | None:
        return _normalize_optional_str(v)

    @model_validator(mode="after")
    def name_min_length_if_set(self) -> DepartmentUpdateRequest:
        if self.name is not None and len(self.name) < 2:
            raise ValueError("name must be at least 2 characters after trimming")
        return self
