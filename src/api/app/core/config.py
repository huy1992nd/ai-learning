from pathlib import Path
from typing import Type

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

_API_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _API_ROOT / ".env"
_PROJECT_ROOT = _API_ROOT.parent.parent


def get_project_root() -> Path:
    return _PROJECT_ROOT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            dotenv_settings,
            env_settings,
            file_secret_settings,
        )

    openai_endpoint: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_ENDPOINT", "AZURE_OPENAI_ENDPOINT"),
    )
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "AZURE_OPENAI_API_KEY"),
    )
    openai_deployment: str = Field(default="gpt-4o-mini", alias="OPENAI_DEPLOYMENT")
    openai_stt_deployment: str = Field(default="", alias="OPENAI_STT_DEPLOYMENT")
    openai_embedding_model: str = Field(default="", alias="OPENAI_EMBEDDING_MODEL")
    openai_embedding_endpoint: str = Field(
        default="",
        validation_alias=AliasChoices(
            "OPENAI_EMBEDDING_ENDPOINT",
            "AZURE_OPENAI_EMBEDDING_ENDPOINT",
        ),
    )
    openai_embedding_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "OPENAI_EMBEDDING_API_KEY",
            "AZURE_OPENAI_EMBEDDING_API_KEY",
        ),
    )
    #: Chỉ dùng khi endpoint là Azure OpenAI: API version REST (vd `2024-02-01`). Để trống → dùng bản mặc định trong code.
    openai_api_version: str = Field(default="", alias="OPENAI_API_VERSION")
    chroma_persist_dir: str = Field(default="dummy/chroma_store", alias="CHROMA_PERSIST_DIR")
    triage_embedding_top_k: int = Field(default=5, alias="TRIAGE_EMBEDDING_TOP_K")
    triage_embedding_confidence_distance: float = Field(
        default=0.25, alias="TRIAGE_EMBEDDING_CONFIDENCE_DISTANCE"
    )

    # SRS v3 — Knowledge Base / RAG (UC-13 … UC-18)
    kb_collection_name: str = Field(default="medassist_knowledge_v1", alias="KB_COLLECTION_NAME")
    rag_retrieval_top_k: int = Field(default=8, alias="RAG_RETRIEVAL_TOP_K")
    rag_similarity_max_distance: float = Field(
        default=1.25,
        alias="RAG_SIMILARITY_MAX_DISTANCE",
        description="Chroma cosine distance upper bound; lower is more similar.",
    )
    kb_max_upload_mb: int = Field(default=10, alias="KB_MAX_UPLOAD_MB")
    rag_chunk_target_tokens: int = Field(default=512, alias="RAG_CHUNK_TARGET_TOKENS")
    rag_chunk_overlap_tokens: int = Field(default=64, alias="RAG_CHUNK_OVERLAP_TOKENS")

    hf_speech_model_id: str = Field(default="google/gemma-4-E4B-it", alias="HF_SPEECH_MODEL_ID")
    hf_speech_model_local_dir: str = Field(default="", alias="HF_SPEECH_MODEL_LOCAL_DIR")
    hf_token: str = Field(default="", alias="HF_TOKEN")
    hf_offline: bool = Field(default=False, alias="HF_OFFLINE")

    audio_tts_engine: str = Field(default="auto", alias="AUDIO_TTS_ENGINE")
    tts_local_voice: str = Field(
        default="vi-VN-HoaiMyNeural",
        validation_alias=AliasChoices("SPEECH_TTS_EDGE_VOICE", "TTS_LOCAL_VOICE"),
    )
    prefer_hf_local_stt: bool = Field(
        default=True,
        validation_alias=AliasChoices("PREFER_HF_LOCAL_STT", "PREFER_GEMMA_STT"),
    )
    default_stt_language: str = Field(default="vi", alias="DEFAULT_STT_LANGUAGE")

    system_prompt: str = Field(default="You are a helpful assistant.", alias="SYSTEM_PROMPT")
    medical_disclaimer: str = Field(
        default=(
            "This information is for reference only and does not replace a professional "
            "medical diagnosis. Always consult a qualified healthcare provider."
        ),
        alias="MEDICAL_DISCLAIMER",
    )
    session_ttl_seconds: int = Field(default=1800, alias="SESSION_TTL_SECONDS")
    session_max_messages: int = Field(default=20, alias="SESSION_MAX_MESSAGES")
    cors_origins: str = Field(
        default="http://localhost:4200,http://127.0.0.1:4200",
        alias="CORS_ORIGINS",
    )
  # Cho phép mọi preview/production *.vercel.app (tránh thiếu origin khi URL đổi)
    cors_origin_regex: str = Field(
        default=r"https://.*\.vercel\.app",
        alias="CORS_ORIGIN_REGEX",
    )
    sqlite_database_path: str = Field(default="dummy/medassist.db", alias="SQLITE_DATABASE_PATH")
    #: Absolute or path relative to `src/api`. Empty → `dummy/kb_uploads` (writable dirs for serverless: e.g. `/tmp/kb_uploads`).
    kb_upload_dir: str = Field(default="", alias="KB_UPLOAD_DIR")
    frontend_base_url: str = Field(default="http://localhost:4200", alias="FRONTEND_BASE_URL")
    teams_webhook_url: str = Field(default="", alias="TEAMS_WEBHOOK_URL")
    jwt_secret: str = Field(default="change-me-in-production-use-long-random-secret", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=120, alias="JWT_EXPIRE_MINUTES")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def effective_embedding_endpoint(self) -> str:
        return self.openai_embedding_endpoint.strip() or self.openai_endpoint.strip()

    def effective_embedding_api_key(self) -> str:
        return self.openai_embedding_api_key.strip() or self.openai_api_key.strip()

    def embedding_configured(self) -> bool:
        return bool(
            self.openai_embedding_model.strip()
            and self.effective_embedding_endpoint()
            and self.effective_embedding_api_key()
        )

    @field_validator("prefer_hf_local_stt", mode="before")
    @classmethod
    def coerce_prefer_hf_local_stt(cls, v: object) -> object:
        if isinstance(v, str):
            t = v.strip().lower()
            if t in ("0", "false", "no", "off", ""):
                return False
            if t in ("1", "true", "yes", "on"):
                return True
            return False
        return v

    @field_validator("hf_offline", mode="before")
    @classmethod
    def coerce_hf_offline(cls, v: object) -> object:
        if isinstance(v, str):
            t = v.strip().lower()
            if t in ("1", "true", "yes", "on"):
                return True
            return False
        return v

    @field_validator(
        "openai_endpoint",
        "openai_api_key",
        "openai_deployment",
        "openai_stt_deployment",
        "openai_embedding_model",
        "openai_embedding_endpoint",
        "openai_embedding_api_key",
        "chroma_persist_dir",
        "cors_origin_regex",
        "kb_upload_dir",
        "hf_speech_model_id",
        "hf_speech_model_local_dir",
        "hf_token",
        "tts_local_voice",
        "audio_tts_engine",
        mode="before",
    )
    @classmethod
    def strip_string_settings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("audio_tts_engine", mode="before")
    @classmethod
    def normalize_audio_tts_engine(cls, v: object) -> object:
        if isinstance(v, str):
            t = v.strip().lower()
            if t in ("auto", "edge"):
                return t
            return "auto"
        return v


def get_settings() -> Settings:
    return Settings()


def resolved_hf_speech_model_path() -> Path:
    s = get_settings()
    raw = (s.hf_speech_model_local_dir or "").strip()
    if raw:
        p = Path(raw)
        return (p if p.is_absolute() else (_PROJECT_ROOT / p)).resolve()
    from app.core.hf_model_cache import hf_repo_safe_dir_name

    mid = (s.hf_speech_model_id or "").strip() or "google/gemma-4-E4B-it"
    return (_PROJECT_ROOT / "models" / hf_repo_safe_dir_name(mid)).resolve()


def hf_speech_stt_dir_ready() -> bool:
    return get_settings().prefer_hf_local_stt
