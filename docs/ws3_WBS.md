# MedAssist AI — Workshop 3: Work Breakdown Structure (WBS)

**Version:** 1.0  
**Date:** 2026-04-22  
**Tham chiếu:** SRS v2.0 (06_MedAssist_AI_SRS_v2)  
**Sprint:** Workshop 3  

---

## Tổng quan Feature

| # | Feature | Priority | SRS Reference |
|---|---------|----------|---------------|
| F1 | Chatbot collect thông tin → lưu Dictionary ở BE → gửi link form pre-fill | P0 — Must Have | UC-05 (FR-05-01 → FR-05-07) |
| F2 | Speech-to-Text hỗ trợ người khiếm thị (Whisper API, tiếng Việt) | P0 — Must Have | UC-12 (FR-12-01 → FR-12-08) |
| F3 | Gửi thông báo đặt lịch tới bác sĩ qua Teams Bot | P2 — Nice to Have | Chưa có trong SRS v2 |

---

## WBS Chi tiết

### 1. F1 — Thu thập thông tin & Pre-filled Registration Form (UC-05)

#### 1.1 Backend — Session Patient Info Dictionary

| ID | Task | FR | Mô tả | Layer |
|----|------|----|-------|-------|
| 1.1.1 | Mở rộng `MedAssistSessionState` dataclass | FR-05-03 | Thêm field `patient_info: dict` vào dataclass. Bao gồm keys: `full_name`, `date_of_birth`, `gender`, `phone`, `email`, `cccd`, `bhyt`, `address`, `department_id`, `department_name`, `doctor_id`, `doctor_name`, `symptoms_summary`, `severity` | BE |
| 1.1.2 | API lưu patient_info vào session state | FR-05-03 | Khi AI validate thành công 1 field → cập nhật `patient_info[field]` trong `MedAssistSessionState` (key = session_id). Tự động include department/doctor info từ UC-04 | BE |
| 1.1.3 | API `GET /api/sessions/{session_id}/patient-info` | FR-05-05 | Tạo route mới trả về patient_info dict từ session state. Response: JSON object chứa tất cả fields đã collect. Return 404 nếu session không tồn tại hoặc hết hạn | BE |
| 1.1.4 | Validation logic cho từng field | FR-05-02 | Implement validate functions: tên (≥2 từ), ngày sinh (dd/mm/yyyy, không tương lai), SĐT (10 số, bắt đầu 0), email (regex), CCCD (12 số). Trả error message bằng ngôn ngữ session | BE |
| 1.1.5 | TTL expiry cho patient_info | FR-05-07 | patient_info nằm trong `MedAssistSessionState` đã có TTL từ `cachetools.TTLCache`. Verify rằng data hết hạn cùng session (24h) | BE |

#### 1.2 Backend — AI Prompt & Conversation Flow

| ID | Task | FR | Mô tả | Layer |
|----|------|----|-------|-------|
| 1.2.1 | Cập nhật system prompt cho stage INFO_COLLECTION | FR-05-01 | Thêm instructions cho AI: thu thập từng field một qua hội thoại tự nhiên, validate ngay, hỏi lại nếu sai format | BE |
| 1.2.2 | Implement conversation state `INFO_COLLECTION` | FR-05-01 | Thêm stage mới trong conversation flow (sau DOCTOR_SELECTION/SLOT_SELECTION). AI biết field nào đã có, field nào cần hỏi tiếp | BE |
| 1.2.3 | Implement conversation state `SEND_REGISTRATION_LINK` | FR-05-04 | Khi tất cả required fields đã collect → AI generate link `{frontend_base_url}/appointment/register?session_id={session_id}` và gửi cho user | BE |
| 1.2.4 | Integrate department/doctor info vào patient_info | FR-05-03 | Sau UC-04, tự động copy `department_id`, `department_name`, `doctor_id`, `doctor_name` vào `patient_info` dict trong session state | BE |

#### 1.3 Frontend — Registration Form Page

| ID | Task | FR | Mô tả | Layer |
|----|------|----|-------|-------|
| 1.3.1 | Tạo route `/appointment/register` | FR-05-04 | Thêm route mới trong `app.routes.ts` với query param `session_id`. Lazy load component | FE |
| 1.3.2 | Tạo component `AppointmentRegisterComponent` | FR-05-05, FR-05-06 | Form Angular Reactive Forms với tất cả fields: họ tên, ngày sinh, giới tính, SĐT, email, CCCD/BHYT, địa chỉ, khoa, bác sĩ, triệu chứng, severity | FE |
| 1.3.3 | Gọi API pre-fill khi load | FR-05-05 | `ngOnInit` → lấy `session_id` từ query param → gọi `GET /api/sessions/{session_id}/patient-info` → populate form fields | FE |
| 1.3.4 | Form validation FE | FR-05-06 | Client-side validation: required fields, format check (SĐT, email, CCCD). Hiển thị error messages | FE |
| 1.3.5 | Submit form → tạo appointment | FR-05-06 | Submit button gọi `POST /api/appointments` với form data. Hiển thị confirmation hoặc error | FE |
| 1.3.6 | UI/UX cho form | FR-05-06 | Responsive layout, Material Design, read-only fields cho khoa/bác sĩ (có thể override), thông báo thành công | FE |
| 1.3.7 | Handle session hết hạn / không tìm thấy | FR-05-07 | Hiển thị thông báo lỗi thân thiện nếu session_id không hợp lệ hoặc đã hết hạn | FE |

#### 1.4 Frontend — Chat Integration

| ID | Task | FR | Mô tả | Layer |
|----|------|----|-------|-------|
| 1.4.1 | Render link trong chat message | FR-05-04 | Khi AI response chứa link `/appointment/register?session_id=...` → render thành clickable button/link trong chat bubble | FE |

---

### 2. F2 — Speech-to-Text (UC-12)

#### 2.1 Backend — Whisper API Integration

| ID | Task | FR | Mô tả | Layer |
|----|------|----|-------|-------|
| 2.1.1 | Verify Whisper API support tiếng Việt | FR-12-03, FR-12-04 | Test OpenAI Whisper `whisper-1` model với audio tiếng Việt. Confirm accuracy. Document kết quả | Research |
| 2.1.2 | Tạo service `speech_to_text_service.py` | FR-12-03 | Implement function `transcribe_audio(file, language) -> str`. Sử dụng `openai.audio.transcriptions.create()` với model `whisper-1` | BE |
| 2.1.3 | Language parameter logic | FR-12-04 | Nếu session language = "vi" → truyền `language="vi"`. Các ngôn ngữ khác → để Whisper auto-detect | BE |
| 2.1.4 | API `POST /api/chat/speech-to-text` | FR-12-02 | Tạo route nhận multipart/form-data (audio file + session_id). Validate file size ≤ 25MB, format (webm/opus/wav). Gọi Whisper service, trả về `{ "text": "..." }` | BE |
| 2.1.5 | Error handling | FR-12-06 | Handle Whisper API errors, empty transcription, timeout. Trả error message thân thiện | BE |

#### 2.2 Frontend — Microphone Recording

| ID | Task | FR | Mô tả | Layer |
|----|------|----|-------|-------|
| 2.2.1 | Thêm nút microphone vào `message-input` | FR-12-01 | Thêm button 🎤 bên cạnh ô nhập tin nhắn. Có `aria-label="Ghi âm giọng nói"` cho screen reader | FE |
| 2.2.2 | Implement audio recording (MediaRecorder API) | FR-12-02 | Sử dụng `navigator.mediaDevices.getUserMedia()` + `MediaRecorder`. Record audio format webm/opus | FE |
| 2.2.3 | Recording state UI | FR-12-08 | Toggle nút microphone: idle → recording (đổi màu đỏ, animation pulse). Hiển thị duration counter | FE |
| 2.2.4 | Gửi audio tới BE | FR-12-02 | Stop recording → tạo Blob → POST multipart/form-data tới `/api/chat/speech-to-text` | FE |
| 2.2.5 | Hiển thị kết quả text | FR-12-05 | Nhận text response → điền vào ô nhập tin nhắn (không tự động gửi). User review/edit rồi nhấn Send | FE |
| 2.2.6 | Permission handling | FR-12-01 | Xử lý trường hợp user deny microphone permission. Hiển thị hướng dẫn cấp quyền | FE |
| 2.2.7 | Error UI | FR-12-06 | Hiển thị toast/snackbar: "Không nhận diện được giọng nói. Vui lòng thử lại hoặc nhập bằng bàn phím." | FE |
| 2.2.8 | File size validation | FR-12-07 | Check audio blob ≤ 25MB trước khi gửi. Cảnh báo nếu quá dài | FE |

---

### 3. F3 — Teams Bot Notification (Nice to Have)

#### 3.1 Backend — Teams Webhook Integration

| ID | Task | FR | Mô tả | Layer |
|----|------|----|-------|-------|
| 3.1.1 | Cấu hình Teams Incoming Webhook | — | Tạo Incoming Webhook trong Teams channel. Lưu URL vào env var `TEAMS_WEBHOOK_URL` | Infra |
| 3.1.2 | Tạo service `teams_notification_service.py` | — | Implement function `send_appointment_notification(appointment_data)`. POST Adaptive Card JSON tới webhook URL | BE |
| 3.1.3 | Thiết kế Adaptive Card template | — | Card hiển thị: mã lịch hẹn, ngày khám, giờ khám, tên bác sĩ, tên khoa, tên bệnh nhân, triệu chứng, severity. Severity URGENT → đánh dấu đỏ | BE |
| 3.1.4 | Trigger notification sau khi tạo appointment | — | Sau `POST /api/appointments` thành công → gọi async `send_appointment_notification()` | BE |
| 3.1.5 | Error handling & fallback | — | Nếu Teams gửi thất bại → log error, không ảnh hưởng appointment flow | BE |
| 3.1.6 | Config env variable | — | Thêm `TEAMS_WEBHOOK_URL` vào `.env`, `config.py`, `docker-compose.yml` | Infra |

---

## Dependency Map

```
1.2.1 ──► 1.2.2 ──► 1.2.3 ──┐
                              │
1.1.1 ──► 1.1.2 ──► 1.1.3 ──┤──► 1.3.3 ──► 1.3.5
                              │
1.1.4 ──────────────────────┘
                              
1.2.4 (after UC-04 integration)

1.3.1 ──► 1.3.2 ──► 1.3.3 ──► 1.3.4 ──► 1.3.5 ──► 1.3.6
                                                      │
1.4.1 (parallel)                                      ▼
                                                   1.3.7

2.1.1 ──► 2.1.2 ──► 2.1.3 ──► 2.1.4 ──► 2.1.5
                                  │
2.2.1 ──► 2.2.2 ──► 2.2.3 ──► 2.2.4 ──► 2.2.5
                                │
                     2.2.6 (parallel)
                     2.2.7 (parallel)
                     2.2.8 (parallel)

3.1.1 ──► 3.1.6 ──► 3.1.2 ──► 3.1.3 ──► 3.1.4 ──► 3.1.5
```

---

## Effort Estimation (Story Points — Fibonacci)

| ID | Task | SP | Ghi chú |
|----|------|----|---------|
| **F1 — Info Collection + Pre-filled Form** | | **34** | |
| 1.1.1 | Mở rộng MedAssistSessionState | 1 | Dataclass change đơn giản |
| 1.1.2 | API lưu patient_info | 3 | Logic tích hợp vào chat flow |
| 1.1.3 | API GET patient-info | 2 | CRUD endpoint đơn giản |
| 1.1.4 | Validation logic | 3 | Nhiều field, mỗi field có rule riêng |
| 1.1.5 | TTL expiry verify | 1 | Chỉ cần test/verify |
| 1.2.1 | System prompt update | 3 | Prompt engineering, test nhiều scenario |
| 1.2.2 | State INFO_COLLECTION | 5 | Core conversation flow logic |
| 1.2.3 | State SEND_REGISTRATION_LINK | 2 | Điều kiện trigger + generate link |
| 1.2.4 | Integrate dept/doctor info | 2 | Copy data giữa states |
| 1.3.1 | Route FE | 1 | Routing config |
| 1.3.2 | Registration form component | 5 | Full reactive form, nhiều fields |
| 1.3.3 | API call pre-fill | 2 | HTTP call + form patch |
| 1.3.4 | Form validation FE | 2 | Mirror BE validation |
| 1.3.5 | Submit appointment | 2 | API call + success/error handling |
| 1.3.6 | UI/UX polish | 3 | Responsive, Material Design |
| 1.3.7 | Error handling (expired session) | 1 | Edge case UI |
| 1.4.1 | Render link in chat | 1 | Rich text parsing |
| **F2 — Speech-to-Text** | | **26** | |
| 2.1.1 | Verify Whisper + tiếng Việt | 2 | Research & test |
| 2.1.2 | STT service | 3 | OpenAI SDK integration |
| 2.1.3 | Language param logic | 1 | Conditional param |
| 2.1.4 | API endpoint STT | 3 | Multipart upload + validation |
| 2.1.5 | Error handling BE | 2 | Multiple error scenarios |
| 2.2.1 | Nút microphone UI | 2 | Button + aria-label + layout |
| 2.2.2 | Audio recording | 5 | MediaRecorder API, browser compat |
| 2.2.3 | Recording state UI | 3 | Animation, state management |
| 2.2.4 | Gửi audio | 2 | FormData + HTTP POST |
| 2.2.5 | Hiển thị text result | 1 | Populate input field |
| 2.2.6 | Permission handling | 1 | Browser permission prompt |
| 2.2.7 | Error UI | 1 | Toast/snackbar |
| 2.2.8 | File size check | 1 | Client-side validation |
| **F3 — Teams Bot (Nice to Have)** | | **10** | |
| 3.1.1 | Cấu hình webhook | 1 | Teams admin setup |
| 3.1.2 | Notification service | 3 | HTTP POST + Adaptive Card |
| 3.1.3 | Card template | 2 | JSON template design |
| 3.1.4 | Trigger after appointment | 2 | Async call integration |
| 3.1.5 | Error handling | 1 | Logging, no-fail |
| 3.1.6 | Config env | 1 | Config files update |
| | **TỔNG** | **70** | |

---

## Suggested Sprint Plan

### Phase 1 — Foundation (Ngày 1-2)
- 2.1.1 Research Whisper + tiếng Việt (kết quả quyết định tiếp tục hay pivot)
- 1.1.1 Mở rộng session state dataclass
- 1.1.4 Validation logic
- 1.3.1 Route FE mới

### Phase 2 — Core BE (Ngày 2-4)
- 1.2.1 + 1.2.2 Conversation flow INFO_COLLECTION
- 1.1.2 Lưu patient_info vào session
- 1.2.4 Tích hợp department/doctor info
- 2.1.2 + 2.1.3 + 2.1.4 Whisper service + API

### Phase 3 — Core FE (Ngày 3-5)
- 1.3.2 + 1.3.3 Registration form + pre-fill
- 2.2.1 + 2.2.2 + 2.2.3 Microphone recording UI
- 1.2.3 SEND_REGISTRATION_LINK state

### Phase 4 — Integration (Ngày 5-6)
- 1.3.4 + 1.3.5 Form validation + submit
- 2.2.4 + 2.2.5 Audio upload + text display
- 1.1.3 API GET patient-info
- 1.4.1 Render link in chat

### Phase 5 — Polish & Nice to Have (Ngày 6-7)
- 1.3.6 + 1.3.7 UI polish + error states
- 2.2.6 + 2.2.7 + 2.2.8 Permission + error + file size
- 2.1.5 BE error handling
- 3.1.x Teams Bot (nếu còn thời gian)

---

## Tech Stack Reference

| Component | Technology | File/Location |
|-----------|-----------|---------------|
| Session State | `cachetools.TTLCache` + dataclass | `app/core/medassist_session_state.py` |
| Chat Route | FastAPI APIRouter | `app/api/routes/chat.py` |
| AI Service | LangChain + OpenAI GPT-4o | `app/services/chat_service.py` |
| Whisper STT | OpenAI `whisper-1` model | `app/services/speech_to_text_service.py` *(mới)* |
| Patient Info API | FastAPI route | `app/api/routes/sessions.py` *(mới)* |
| FE Chat Input | Angular component | `src/app/features/chat/message-input/` |
| FE Form | Angular Reactive Forms | `src/app/features/appointment-register/` *(mới)* |
| FE Routing | Angular Router | `src/app/app.routes.ts` |
| Teams Notification | HTTP Webhook | `app/services/teams_notification_service.py` *(mới, nice to have)* |

---

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Whisper API không chính xác với tiếng Việt | Cao | Task 2.1.1 verify sớm. Fallback: Web Speech API browser-native |
| Browser không hỗ trợ MediaRecorder | Trung bình | Check browser compat, hiển thị fallback message |
| Session hết hạn giữa chừng khi user mở form | Thấp | Task 1.3.7 hiển thị error + hướng dẫn quay lại chat |
| Teams Webhook bị block bởi IT policy | Thấp | Nice to have, có thể bỏ qua |
