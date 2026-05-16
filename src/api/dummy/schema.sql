-- MedAssist AI — SQLite schema (see docs/ba_documents/03_MedAssist_AI_Technical Specification.docx)
-- Table order: appointments before medical_examination_schedule (FK).

PRAGMA foreign_keys = ON;

-- Departments
CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT,
    specialty   TEXT,
    symptoms_keywords TEXT,
    common_diseases TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Disease → department mapping
CREATE TABLE IF NOT EXISTS disease_department_mapping (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_name  TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Doctors
CREATE TABLE IF NOT EXISTS doctors (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    title         TEXT,
    specialty     TEXT,
    bio           TEXT,
    photo_url     TEXT,
    email         TEXT UNIQUE NOT NULL,
    phone         TEXT,
    is_active     INTEGER DEFAULT 1,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Default weekly working hours (0=Mon … 6=Sun)
CREATE TABLE IF NOT EXISTS doctor_working_hours (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id   INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    start_time  TEXT NOT NULL,
    end_time    TEXT NOT NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);

-- Patients (typically inserted when appointment is confirmed; seed may include demo rows)
CREATE TABLE IF NOT EXISTS patients (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name    TEXT NOT NULL,
    dob          DATE,
    gender       TEXT,
    phone        TEXT NOT NULL,
    email        TEXT,
    id_number    TEXT,
    insurance_id TEXT,
    address      TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Appointments
CREATE TABLE IF NOT EXISTS appointments (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_code   TEXT UNIQUE NOT NULL,
    patient_id         INTEGER NOT NULL,
    doctor_id          INTEGER NOT NULL,
    department_id      INTEGER NOT NULL,
    symptoms           TEXT,
    predicted_diseases TEXT,
    severity           TEXT NOT NULL,
    scheduled_at       DATETIME NOT NULL,
    status             TEXT DEFAULT 'PENDING',
    notes              TEXT,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Booked / blocked slots (UTC)
CREATE TABLE IF NOT EXISTS medical_examination_schedule (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id      INTEGER NOT NULL,
    start_datetime DATETIME NOT NULL,
    end_datetime   DATETIME NOT NULL,
    status         TEXT NOT NULL DEFAULT 'BOOKED',
    appointment_id INTEGER,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);

-- Chat sessions (session_id from frontend)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id           TEXT PRIMARY KEY,
    language     TEXT DEFAULT 'en',
    patient_id   INTEGER,
    messages     TEXT,
    context      TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at   DATETIME NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Admin / doctor portal
CREATE TABLE IF NOT EXISTS user_accounts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL,
    doctor_id     INTEGER,
    is_active     INTEGER DEFAULT 1,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);

CREATE INDEX IF NOT EXISTS idx_schedule_doctor_datetime
    ON medical_examination_schedule(doctor_id, start_datetime);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor
    ON appointments(doctor_id, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_sessions_expires
    ON chat_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_disease_mapping_department
    ON disease_department_mapping(department_id);
CREATE INDEX IF NOT EXISTS idx_doctors_department
    ON doctors(department_id);

-- Workshop 4 / SRS v3 — Medical Knowledge Base & RAG (UC-13 … UC-18)
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT NOT NULL,
    category            TEXT NOT NULL,
    original_filename   TEXT NOT NULL DEFAULT '',
    content_text        TEXT NOT NULL DEFAULT '',
    file_path           TEXT,
    mime_type           TEXT,
    status              TEXT NOT NULL DEFAULT 'PENDING',
    total_chunks        INTEGER NOT NULL DEFAULT 0,
    metadata_json       TEXT,
    processing_error    TEXT,
    uploaded_by         TEXT,
    is_active           INTEGER NOT NULL DEFAULT 1,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id         INTEGER NOT NULL,
    chunk_index         INTEGER NOT NULL,
    content             TEXT NOT NULL,
    token_count         INTEGER,
    embedding_status    TEXT NOT NULL DEFAULT 'PENDING',
    vector_id           TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rag_query_logs (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id              TEXT,
    query_text              TEXT NOT NULL,
    retrieved_chunk_ids     TEXT,
    retrieved_scores        TEXT,
    final_response          TEXT,
    latency_ms              INTEGER,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_documents_category
    ON knowledge_documents(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_status
    ON knowledge_documents(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_active
    ON knowledge_documents(is_active);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document
    ON knowledge_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_rag_logs_created
    ON rag_query_logs(created_at);
