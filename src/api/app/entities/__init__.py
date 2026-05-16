"""SQLAlchemy ORM entities mapping SQLite tables (see `dummy/schema.sql`)."""

from app.entities.appointment import AppointmentEntity
from app.entities.chat_session import ChatSessionEntity
from app.entities.department import DepartmentEntity
from app.entities.knowledge_chunk import KnowledgeChunkEntity
from app.entities.knowledge_document import KnowledgeDocumentEntity
from app.entities.disease_department_mapping import DiseaseDepartmentMappingEntity
from app.entities.doctor import DoctorEntity
from app.entities.doctor_working_hour import DoctorWorkingHourEntity
from app.entities.medical_examination_schedule import MedicalExaminationScheduleEntity
from app.entities.patient import PatientEntity
from app.entities.rag_query_log import RagQueryLogEntity
from app.entities.user_account import UserAccountEntity

TABLE_NAMES: frozenset[str] = frozenset(
    {
        "appointments",
        "chat_sessions",
        "departments",
        "disease_department_mapping",
        "doctor_working_hours",
        "doctors",
        "knowledge_chunks",
        "knowledge_documents",
        "medical_examination_schedule",
        "patients",
        "rag_query_logs",
        "user_accounts",
    }
)

__all__ = [
    "AppointmentEntity",
    "ChatSessionEntity",
    "DepartmentEntity",
    "DiseaseDepartmentMappingEntity",
    "DoctorEntity",
    "DoctorWorkingHourEntity",
    "KnowledgeChunkEntity",
    "KnowledgeDocumentEntity",
    "MedicalExaminationScheduleEntity",
    "PatientEntity",
    "RagQueryLogEntity",
    "TABLE_NAMES",
    "UserAccountEntity",
]
