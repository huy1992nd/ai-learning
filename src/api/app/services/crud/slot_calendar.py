"""
Fixed clinic slots: next 7 calendar days, Mon-Fri only, 8 one-hour blocks per day.
Morning 08:00-12:00 (4), afternoon 13:30-17:30 (4). Asia/Ho_Chi_Minh wall time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.medical_examination_schedule import MedicalExaminationScheduleEntity

VN = ZoneInfo("Asia/Ho_Chi_Minh")

SLOT_HOURS: list[tuple[int, int]] = [
    (8, 0),
    (9, 0),
    (10, 0),
    (11, 0),
    (13, 30),
    (14, 30),
    (15, 30),
    (16, 30),
]


@dataclass
class BookableSlot:
    slot_index: int
    start_local: datetime
    day: date
    label: str

    @property
    def storage_value(self) -> str:
        return self.start_local.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")


def _next_weekdays_7() -> list[date]:
    out: list[date] = []
    d = datetime.now(VN).date()
    for _ in range(14):
        if len(out) >= 7:
            break
        if d.weekday() < 5:
            out.append(d)
        d = d + timedelta(days=1)
    return out


def _slot_datetimes_on_day(d: date) -> list[BookableSlot]:
    out: list[BookableSlot] = []
    for i, (h, m) in enumerate(SLOT_HOURS, start=1):
        dt = datetime(d.year, d.month, d.day, h, m, 0, tzinfo=VN)
        out.append(BookableSlot(slot_index=i, start_local=dt, day=d, label=dt.strftime("%Y-%m-%d %H:%M")))
    return out


def list_all_rule_slots_for_next_week() -> list[BookableSlot]:
    slots: list[BookableSlot] = []
    for d in _next_weekdays_7():
        slots.extend(_slot_datetimes_on_day(d))
    return slots


def list_available_slots_for_doctor(
    db: Session, doctor_id: int, *, from_now: bool = True
) -> list[BookableSlot]:
    now = datetime.now(VN)
    all_slots = list_all_rule_slots_for_next_week()
    free: list[BookableSlot] = []
    for s in all_slots:
        if from_now and s.start_local < now:
            continue
        start_naive = s.start_local.replace(tzinfo=None)
        end_naive = start_naive + timedelta(hours=1)
        clash_stmt = (
            select(MedicalExaminationScheduleEntity.id)
            .where(MedicalExaminationScheduleEntity.doctor_id == doctor_id)
            .where(MedicalExaminationScheduleEntity.start_datetime < end_naive)
            .where(MedicalExaminationScheduleEntity.end_datetime > start_naive)
            .limit(1)
        )
        clash = db.execute(clash_stmt).first()
        if not clash:
            free.append(s)
    return free
