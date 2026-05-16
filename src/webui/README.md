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
4. **Output Directory:** **`dist/webui/browser`** — bắt buộc có `/browser` (file `index.html` nằm ở đó; log build chỉ ghi `dist/webui` là thư mục cha). Nếu để `dist/webui` → deploy xong mở web **404 NOT_FOUND**. Có thể để trống trong dashboard nếu dùng [`vercel.json`](./vercel.json) (`outputDirectory` đã khai báo).
5. **Install Command:** `npm ci` (khuyến nghị) hoặc `npm install`.

### 2. Nối API backend

Production gọi **thẳng ngrok** trong [`environment.prod.ts`](./src/environments/environment.prod.ts) (`apiBaseUrl: https://…ngrok-free.dev/api`). Trên Network tab bạn sẽ thấy request tới host ngrok, không còn `…vercel.app/api/…` (tránh lỗi Vercel **502 / DNS_HOSTNAME_EMPTY** khi rewrite proxy).

**Bắt buộc trên BE** (`src/api/.env`): `CORS_ORIGINS` phải có URL FE Vercel, ví dụ:

`CORS_ORIGINS=http://localhost:4200,https://ai-learning-web-git-main-huy1992nds-projects.vercel.app`

Tunnel ngrok phải **đang chạy**; URL đổi thì sửa `environment.ts`, `environment.prod.ts` và redeploy FE.

### 3. Kiểm tra

Sau deploy: mở URL Vercel của FE, thử chat / health. Nếu lỗi mạng, mở DevTools → Network và kiểm tra request tới `/api` hoặc tới host BE.

### 4. Ghi chú

- SSE chat dùng `fetch` tới `apiBaseUrl`; CORS và (nếu dùng rewrite) URL BE phải đúng.
- Không cần deploy BE trên Vercel nếu BE chạy chỗ khác (Docker, Railway, …); chỉ cần URL công khai + CORS.
