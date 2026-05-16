#!/usr/bin/env python3
"""Create SQLite file `medassist.db` under `dummy/` and load sample data."""

from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

try:
    import bcrypt
except ImportError:
    print("Install bcrypt: pip install bcrypt", file=sys.stderr)
    sys.exit(1)

DUMMY_DIR = Path(__file__).resolve().parent
DB_PATH = DUMMY_DIR / "medassist.db"
SCHEMA_PATH = DUMMY_DIR / "schema.sql"
# Embedding cache dir: dummy/chroma_store
CHROMA_DIR = DUMMY_DIR / "chroma_store"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _apply_schema(conn: sqlite3.Connection) -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)


def _seed(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.executemany(
        """
        INSERT INTO departments (
            id, name, description, specialty, symptoms_keywords, common_diseases
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                1,
                "Department of Cardiology",
                "Diagnosis, treatment, and follow-up care for heart disease, hypertension, chest pain, and rhythm disorders.",
                "Cardiology",
                "chest pain, đau ngực, palpitations, đánh trống ngực, shortness of breath, khó thở khi gắng sức, hypertension, huyết áp cao, irregular heartbeat, tim đập không đều",
                "Hypertension, Angina pectoris, Cardiac arrhythmia, Heart failure",
            ),
            (
                2,
                "Department of Gastroenterology",
                "Care for digestive tract, liver, gallbladder, and pancreas disorders, including endoscopy-based evaluation.",
                "Gastroenterology",
                "abdominal pain, đau bụng, bloating, đầy hơi, acid reflux, trào ngược dạ dày, heartburn, ợ nóng, nausea, buồn nôn, diarrhea, tiêu chảy",
                "Gastroesophageal reflux disease, Peptic ulcer, Irritable bowel syndrome, Hepatitis, Gallstones",
            ),
            (
                3,
                "Department of Pulmonology",
                "Assessment and treatment of lung and airway diseases such as asthma, COPD, bronchitis, and pneumonia.",
                "Pulmonology",
                "cough, ho, wheezing, khò khè, shortness of breath, khó thở, chest tightness, tức ngực, sputum, đàm, prolonged cough, ho kéo dài",
                "Bronchitis, Asthma, Pneumonia, Chronic obstructive pulmonary disease",
            ),
            (
                4,
                "Department of General Internal Medicine",
                "First-line medical evaluation, chronic disease monitoring, and coordination of care for complex adult conditions.",
                "Internal medicine",
                "fever, sốt, fatigue, mệt mỏi, dizziness, chóng mặt, general weakness, suy nhược, unclear symptoms, triệu chứng không rõ, chronic disease follow-up, theo dõi bệnh mạn",
                "Influenza, Diabetes mellitus, Hyperlipidemia, Anemia",
            ),
            (
                5,
                "Department of Otolaryngology",
                "Care for ear, nose, and throat conditions, including sore throat, sinusitis, hearing issues, and vertigo.",
                "Otolaryngology",
                "sore throat, đau họng, ear pain, đau tai, nasal congestion, nghẹt mũi, sinus pain, đau xoang, hearing loss, giảm thính lực, vertigo, chóng mặt xoay",
                "Acute pharyngitis, Sinusitis, Otitis media, Vertigo",
            ),
            (
                6,
                "Department of Pediatrics",
                "Medical care for infants, children, and adolescents, including fever, infections, vaccination, and growth concerns.",
                "Pediatrics",
                "child fever, sốt ở trẻ, rash in child, phát ban ở trẻ, poor feeding, bú kém, vomiting in child, nôn ở trẻ, cough in child, ho ở trẻ, growth concerns, chậm tăng cân",
                "Pediatric fever, Hand, foot, and mouth disease, Childhood asthma",
            ),
            (
                7,
                "Department of Obstetrics and Gynecology",
                "Women's health services, pregnancy care, menstrual disorders, contraception counseling, and gynecologic conditions.",
                "Obstetrics and Gynecology",
                "pregnancy checkup, khám thai, irregular menstruation, kinh nguyệt không đều, pelvic pain, đau vùng chậu, vaginal discharge, khí hư bất thường, menstrual pain, đau bụng kinh, prenatal care, chăm sóc trước sinh",
                "Pregnancy-related care, Dysmenorrhea, Vaginitis",
            ),
            (
                8,
                "Department of Neurology",
                "Evaluation and management of brain, nerve, and muscle conditions such as headache, stroke, seizures, and numbness.",
                "Neurology",
                "headache, đau đầu, numbness, tê bì, weakness, yếu liệt, seizure, co giật, speech difficulty, nói khó, memory problems, suy giảm trí nhớ",
                "Migraine, Stroke, Epilepsy",
            ),
            (
                9,
                "Department of Rheumatology",
                "Care for joint pain, arthritis, autoimmune diseases, gout, and connective tissue disorders.",
                "Rheumatology",
                "joint pain, đau khớp, joint swelling, sưng khớp, morning stiffness, cứng khớp buổi sáng, back pain, đau lưng, gout flare, cơn gout cấp, autoimmune symptoms, triệu chứng tự miễn",
                "Rheumatoid arthritis, Gout, Systemic lupus erythematosus",
            ),
            (
                10,
                "Department of Dermatology",
                "Diagnosis and treatment of skin, hair, and nail conditions, including rashes, acne, eczema, and skin infections.",
                "Dermatology",
                "rash, phát ban, itching, ngứa, acne, mụn trứng cá, eczema, chàm, skin redness, đỏ da, fungal rash, nấm da",
                "Atopic dermatitis, Acne vulgaris, Fungal skin infection",
            ),
            (
                11,
                "Department of Urology",
                "Care for urinary tract, kidney, bladder, prostate, and male reproductive health conditions.",
                "Urology",
                "painful urination, tiểu buốt, frequent urination, tiểu nhiều lần, blood in urine, tiểu máu, flank pain, đau hông lưng, urinary retention, bí tiểu, lower urinary symptoms, rối loạn tiểu tiện",
                "Urinary tract infection, Kidney stones, Benign prostatic hyperplasia",
            ),
            (
                12,
                "Department of Emergency Medicine",
                "Immediate assessment and stabilization for urgent or life-threatening symptoms, trauma, severe pain, and acute illness.",
                "Emergency Medicine",
                "severe chest pain, đau ngực dữ dội, severe shortness of breath, khó thở cấp, anaphylaxis, phản vệ, major trauma, chấn thương nặng, loss of consciousness, bất tỉnh, heavy bleeding, chảy máu nhiều",
                "Severe chest pain, Anaphylaxis, Major trauma",
            ),
        ],
    )

    mappings = [
        ("Hypertension", 1),
        ("Angina pectoris", 1),
        ("Cardiac arrhythmia", 1),
        ("Heart failure", 1),
        ("Gastroesophageal reflux disease", 2),
        ("Peptic ulcer", 2),
        ("Irritable bowel syndrome", 2),
        ("Hepatitis", 2),
        ("Gallstones", 2),
        ("Bronchitis", 3),
        ("Asthma", 3),
        ("Pneumonia", 3),
        ("Chronic obstructive pulmonary disease", 3),
        ("Influenza", 4),
        ("Diabetes mellitus", 4),
        ("Hyperlipidemia", 4),
        ("Anemia", 4),
        ("Acute pharyngitis", 5),
        ("Sinusitis", 5),
        ("Otitis media", 5),
        ("Vertigo", 5),
        ("Pediatric fever", 6),
        ("Hand, foot, and mouth disease", 6),
        ("Childhood asthma", 6),
        ("Pregnancy-related care", 7),
        ("Dysmenorrhea", 7),
        ("Vaginitis", 7),
        ("Migraine", 8),
        ("Stroke", 8),
        ("Epilepsy", 8),
        ("Rheumatoid arthritis", 9),
        ("Gout", 9),
        ("Systemic lupus erythematosus", 9),
        ("Atopic dermatitis", 10),
        ("Acne vulgaris", 10),
        ("Fungal skin infection", 10),
        ("Urinary tract infection", 11),
        ("Kidney stones", 11),
        ("Benign prostatic hyperplasia", 11),
        ("Severe chest pain", 12),
        ("Anaphylaxis", 12),
        ("Major trauma", 12),
    ]
    cur.executemany(
        "INSERT INTO disease_department_mapping (disease_name, department_id) VALUES (?, ?)",
        mappings,
    )

    doctors = [
        (1, "James Miller", 1, "MD, FACC", "Interventional cardiology", "15 years of experience in clinical cardiology.", None, "james.miller@hospital.demo", "0901000001", 1),
        (2, "Sarah Chen", 1, "MD", "Hypertension", None, None, "sarah.chen@hospital.demo", "0901000002", 1),
        (3, "David Park", 2, "MD, PhD", "Gastroenterology", "Focus on digestive endoscopy.", None, "david.park@hospital.demo", "0901000003", 1),
        (4, "Emily Roberts", 2, "MD", "Hepatology", None, None, "emily.roberts@hospital.demo", "0901000004", 1),
        (5, "Michael Brown", 3, "MD, PhD", "Pulmonology", None, None, "michael.brown@hospital.demo", "0901000005", 1),
        (6, "Lisa Wang", 3, "MD", "Asthma, COPD", None, None, "lisa.wang@hospital.demo", "0901000006", 1),
        (7, "Anna Thompson", 4, "MD", "General internal medicine", None, None, "anna.thompson@hospital.demo", "0901000007", 1),
        (8, "Robert Lee", 5, "MD", "Otolaryngology", None, None, "robert.lee@hospital.demo", "0901000008", 1),
    ]
    cur.executemany(
        """
        INSERT INTO doctors (
            id, full_name, department_id, title, specialty, bio, photo_url,
            email, phone, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        doctors,
    )

    hours = []
    for doc_id in range(1, 9):
        for dow in range(0, 5):
            hours.append((doc_id, dow, "08:00", "17:00"))
    cur.executemany(
        """
        INSERT INTO doctor_working_hours (doctor_id, day_of_week, start_time, end_time)
        VALUES (?, ?, ?, ?)
        """,
        hours,
    )

    cur.executemany(
        """
        INSERT INTO patients (id, full_name, dob, gender, phone, email, address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "Mary Johnson", "1990-05-12", "FEMALE", "0912000001", "mary.johnson@email.demo", "Hanoi, Vietnam"),
            (2, "John Smith", "1985-11-03", "MALE", "0912000002", "john.smith@email.demo", "Ho Chi Minh City, Vietnam"),
        ],
    )

    cur.execute(
        """
        INSERT INTO appointments (
            id, appointment_code, patient_id, doctor_id, department_id,
            symptoms, predicted_diseases, severity, scheduled_at, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,
            "MA-20260418-0001",
            1,
            1,
            1,
            '["left-sided chest pain on exertion", "mild shortness of breath"]',
            '[{"name": "Stable angina", "confidence": 0.72}]',
            "MODERATE",
            "2026-04-22 09:00:00",
            "CONFIRMED",
            "Demo appointment created by seed script.",
        ),
    )

    cur.execute(
        """
        INSERT INTO medical_examination_schedule (
            doctor_id, start_datetime, end_datetime, status, appointment_id
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (1, "2026-04-22 09:00:00", "2026-04-22 10:00:00", "BOOKED", 1),
    )

    cur.execute(
        """
        INSERT INTO chat_sessions (
            id, language, patient_id, messages, context, expires_at
        ) VALUES (?, ?, ?, ?, ?, datetime('now', '+1 day'))
        """,
        (
            "550e8400-e29b-41d4-a716-446655440000",
            "en",
            None,
            "[]",
            '{"stage": "SYMPTOM_COLLECTION", "collected_info": {}}',
        ),
    )

    admin_hash = bcrypt.hashpw(b"Demo@123", bcrypt.gensalt()).decode("ascii")
    doctor_hash = bcrypt.hashpw(b"Demo@123", bcrypt.gensalt()).decode("ascii")
    cur.execute(
        """
        INSERT INTO user_accounts (email, password_hash, role, doctor_id, is_active)
        VALUES (?, ?, 'ADMIN', NULL, 1)
        """,
        ("admin@medassist.local", admin_hash),
    )
    cur.execute(
        """
        INSERT INTO user_accounts (email, password_hash, role, doctor_id, is_active)
        VALUES (?, ?, 'DOCTOR', ?, 1)
        """,
        ("doctor@medassist.local", doctor_hash, 1),
    )

    conn.commit()


def main() -> None:
    if not SCHEMA_PATH.is_file():
        print(f"Schema file not found: {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(1)

    if DB_PATH.exists():
        DB_PATH.unlink()
    chroma_wiped = False
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR, ignore_errors=True)
        chroma_wiped = True

    conn = _connect()
    try:
        _apply_schema(conn)
        _seed(conn)
    finally:
        conn.close()

    print(f"Database created: {DB_PATH}")
    if chroma_wiped:
        print(f"Chroma store wiped: {CHROMA_DIR}")
    print("Demo admin account: admin@medassist.local / Demo@123")
    print("Demo doctor account: doctor@medassist.local / Demo@123 (doctor_id=1, James Miller)")


if __name__ == "__main__":
    main()
