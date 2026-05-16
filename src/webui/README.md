# Angular v21 Chatbot Frontend

Angular v21 standalone app using Angular Material. Talks to the FastAPI
backend over Server-Sent Events for streaming chat responses.

## Prerequisites
- Node.js 20+
- npm 10+
- Backend running at `http://localhost:8000` (see `../api/README.md`).

## Setup
```bash
cd src/webui
npm install
```

## Run (development)
```bash
npm start
```

The dev server runs on `http://localhost:4200`. Chat requests use the URL in
[`environment.ts`](./src/environments/environment.ts) (`apiBaseUrl`, mặc định tunnel **ngrok** tới BE) so **SSE streams are not
buffered** by the dev proxy — tokens appear one-by-one in the UI. Đổi `apiBaseUrl` về `http://localhost:8000/api` nếu chạy BE local không tunnel. The backend
must allow CORS from `http://localhost:4200` (already configured in `src/api`).
`proxy.conf.json` is still available if you switch `apiBaseUrl` back to a
relative `/api`.

## Key files
- `src/app/core/services/session.service.ts` — generates a UUID on first
  load, persists it to `sessionStorage`, and handles "new conversation"
  rotation (also calls `DELETE /api/sessions/{id}` on the backend).
- `src/app/core/services/chat-session.store.ts` — sends messages to
  `POST /api/chat/stream` and consumes the SSE response via
  `fetch` + `ReadableStream`. Exposes `messages`, `isStreaming`, `stage`,
  `language`, and `severity` signals.
- `src/app/features/chatbot-widget/chatbot-widget.ts` — floating chatbot
  widget (FAB + overlay window) that hosts the message list and composer.
- `src/app/features/chat/message-list/message-list.component.ts` — renders
  the bubble list (with markdown via `RichTextPipe`) and auto-scrolls on
  updates.
- `src/app/features/chat/message-input/message-input.component.ts` — textarea
  + send/stop buttons. Enter sends, Shift+Enter inserts a newline.

## Deploy lên Vercel (chỉ frontend)

Angular build ra static files; Vercel phát từ thư mục output.

### 1. Cấu hình project Vercel

1. **Root Directory** = `src/webui` (monorepo) — hoặc để trống nếu repo chỉ chứa thư mục webui ở gốc.
2. **Framework Preset:** Angular (Vercel thường tự nhận qua `angular.json`).
3. **Build Command:** `npm run build` (mặc định).
4. **Output Directory:** `dist/webui/browser` (builder `@angular/build:application` của Angular 17+).
5. **Install Command:** `npm ci` (khuyến nghị) hoặc `npm install`.

### 2. Nối API backend

Production đang dùng `apiBaseUrl: '/api'` trong [`environment.prod.ts`](./src/environments/environment.prod.ts).

**Cách A — proxy qua Vercel (giữ `/api` trên cùng domain FE):** [`vercel.json`](./vercel.json) rewrite `/api` → BE (hiện trỏ tunnel ngrok; đổi khi URL tunnel đổi). BE phải bật **CORS** cho origin FE (ví dụ `https://your-app.vercel.app`).

**Cách B — gọi thẳng URL BE:** đổi `apiBaseUrl` trong `environment.prod.ts` thành `https://<be-host>/api`, commit rồi build; BE vẫn phải CORS cho origin FE.

### 3. Kiểm tra

Sau deploy: mở URL Vercel của FE, thử chat / health. Nếu lỗi mạng, mở DevTools → Network và kiểm tra request tới `/api` hoặc tới host BE.

### 4. Ghi chú

- SSE chat dùng `fetch` tới `apiBaseUrl`; CORS và (nếu dùng rewrite) URL BE phải đúng.
- Không cần deploy BE trên Vercel nếu BE chạy chỗ khác (Docker, Railway, …); chỉ cần URL công khai + CORS.
