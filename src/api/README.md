# FastAPI Chatbot Backend

FastAPI service that proxies OpenAI-compatible chat completions back to the client
over Server-Sent Events (SSE). Conversation context is kept per `session_id`
in an in-memory TTL cache (no database).

## Prerequisites
- Python 3.11+
- An OpenAI-compatible endpoint with a chat deployment (for example `gpt-4o-mini`). Optional: local STT via Hugging Face (`HF_SPEECH_MODEL_ID`, cached under the repo `models/`), and TTS via edge-tts (`SPEECH_TTS_EDGE_VOICE` / `TTS_LOCAL_VOICE`).

## Setup
```bash
cd src/api
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # on Windows
# cp .env.example .env   # on macOS / Linux
```

Edit **`.env` in this folder** (`src/api/.env`). The app always loads that file
regardless of which directory you run `uvicorn` from. With the default Pydantic
settings source order, **OS env would override `.env`**; this project customizes
the order so **values in `src/api/.env` win over the same variable in the OS**
( handy when an old API key is still set in Windows user/system env).

## Dummy SQLite database

Optional **demo SQLite** (departments, doctors, disease mapping, …). It is used **only inside the backend** when handling `POST /api/chat/stream` (gợi ý khoa/bác sĩ sau bước dự đoán bệnh). The frontend does **not** call separate `/api/departments` APIs.

| Item | Path / note |
|------|----------------|
| Schema | `dummy/schema.sql` |
| Seed script | `dummy/seed.py` (requires `bcrypt` from `requirements.txt`) |
| Database file | `dummy/medassist.db` (created by seed; listed in `.gitignore`) |
| Config | `SQLITE_DATABASE_PATH` in `.env` (default: `dummy/medassist.db`, relative to `src/api`) |

**Create / refresh the database** (from `src/api` with venv activated):

```bash
python dummy/seed.py
```

This deletes any existing `dummy/medassist.db`, reapplies the schema, and loads English sample data. Demo admin (for future auth): `admin@medassist.local` / `Demo@123`.

**Check connectivity** while the API is running:

```bash
curl -s http://localhost:8000/api/db/ping
```

You should see `"ok": true` and the resolved database path.

## Run
```bash
uvicorn app.main:app --reload --reload-include ".env" --port 8000
```

The `--reload-include ".env"` line makes the dev server restart when you change
`.env` (otherwise `--reload` often only watches `.py` files).

The API is then available at `http://localhost:8000`.

## Deploy lên Vercel

Repo này dùng **FastAPI + PyTorch/Transformers + Chroma + SQLite**. Trên Vercel, entry ASGI là [`main.py`](./main.py) (re-export `app` từ `app.main`); cài gói bằng **`pip install -r requirements.txt`** (xem [`vercel.json`](./vercel.json)) để tránh lỗi `uv lock` khi không dùng đủ bảng `[project]` trong `pyproject.toml`. Lưu ý:

- **Kích thước & cold start:** `torch` + `transformers` gần giới hạn bundle Python trên Vercel; lần khởi động có thể rất chậm. Nếu build/deploy lỗi vì dung lượng, nên dùng **Docker** (file [`Dockerfile`](./Dockerfile)) trên Fly.io, Railway hoặc Google Cloud Run.
- **Filesystem:** trên serverless chỉ nên ghi **`/tmp`**. Đặt biến môi trường (trong Vercel → Settings → Environment Variables) ví dụ:
  - `SQLITE_DATABASE_PATH=/tmp/medassist.db`
  - `CHROMA_PERSIST_DIR=/tmp/chroma_store`
  - `KB_UPLOAD_DIR=/tmp/kb_uploads`
- **Seed:** lần đầu file SQLite chưa có, app gọi `seed_if_missing()` trong lifespan để tạo DB demo (cùng logic schema/seed như `python dummy/seed.py`).
- **STT local HF:** trên Vercel không thực tế (tải mô hình lớn). Đặt `PREFER_HF_LOCAL_STT=0` và cấu hình `OPENAI_STT_DEPLOYMENT` (Whisper) nếu cần STT.
- **SSE / thời gian chạy:** luồng chat dài có thể chạm giới hạn thời gian function; trên plan Pro có thể tăng `maxDuration` trong dashboard nếu cần.

**Các bước**

1. Cài [Vercel CLI](https://vercel.com/docs/cli) (`npm i -g vercel`) hoặc import repo trên [vercel.com](https://vercel.com).
2. **Root Directory** (Vercel → Project → **Settings** → **Build and Deployment** → **Root Directory**):
   - Repo **monorepo** giống `ai-learning` (có thư mục `src/api/` trên GitHub): nhập đúng `src/api` — **không** có dấu chấm cuối (`src/api.` sẽ lỗi), **không** thêm `/` đầu.
   - Repo **chỉ chứa backend** (ví dụ đã copy nội dung `src/api` lên **gốc** repo `…-vercel-demo`): để Root Directory **trống** hoặc `.` (không dùng `src/api` vì trên GitHub không có đường dẫn đó).
   - Cách kiểm nhanh: trên GitHub mở repo → nếu thấy `requirements.txt` và `main.py` ngay ở gốc thì Root Directory để trống; nếu các file nằm trong `src/api/` thì Root Directory = `src/api`.
3. Biến môi trường: **Settings** → **Environment Variables** (không dùng tab Deployments để set root).
4. Thêm secrets OpenAI/Azure (và các biến như mục Filesystem/STT ở trên). `JWT_SECRET` phải đổi khỏi giá trị demo.
5. Deploy: push commit (Git) hoặc `vercel` từ máy sau khi `vercel login`.

Sau deploy, kiểm tra `GET /api/health` và `GET /api/db/ping` trên URL Vercel (đường dẫn gốc `/` có thể 404 — đó là bình thường nếu không có trang tĩnh).

**Lưu ý:** Không ai (kể cả công cụ AI) có thể đăng nhập Vercel/GitHub thay bạn. Nếu build vẫn lỗi, copy **toàn bộ log build** (tab Deployment → failed build → Building) và gửi lại để xử lý tiếp.

## Endpoints
| Method | Path                         | Description                                     |
|--------|------------------------------|-------------------------------------------------|
| GET    | `/api/health`                | Liveness probe.                                 |
| GET    | `/api/db/ping`               | SQLite file exists and accepts a test query.    |
| POST   | `/api/chat/stream`           | SSE stream of assistant tokens for a session.   |
| POST   | `/api/audio/speech-to-text`  | Multipart STT: `session_id`, `file` → `{ "text" }`. |
| POST   | `/api/audio/text-to-speech`  | JSON TTS: `text`, optional `voice`, `response_format` → audio. |
| DELETE | `/api/sessions/{session_id}` | Clear the in-memory context for a session.      |

### `POST /api/chat/stream`
**Đây là endpoint duy nhất FE cần cho hội thoại.** Trên server, trước khi stream câu trả lời, BE tự chạy nội bộ: topic guard (UC-00), detect ngôn ngữ (UC-01), trích triệu chứng (UC-02), gợi ý bệnh tham khảo (UC-03), tra SQLite gợi ý khoa/bác sĩ (UC-04) — rồi ghép ngữ cảnh vào system prompt và gọi OpenAI-compatible streaming.

Request body:
```json
{ "session_id": "uuid-from-frontend", "message": "Hello!" }
```

Response is an `text/event-stream`:
```
data: {"token": "Hi"}

data: {"token": "!"}

event: done
data: [DONE]
```

Errors are emitted as an `event: error` SSE frame with a JSON body.

## Notes
- Session history lives only in RAM. Restarting the process wipes all
  conversations. Adjust `SESSION_TTL_SECONDS` and `SESSION_MAX_MESSAGES` in
  `.env` to tune retention.
- The user and assistant messages for a turn are only persisted into the
  session store after the assistant finishes streaming successfully, so
  aborted / failed turns do not pollute future context.
