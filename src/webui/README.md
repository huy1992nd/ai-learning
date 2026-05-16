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

The dev server runs on `http://localhost:4200`. Chat requests use
`http://localhost:8000/api` directly (`environment.ts`) so **SSE streams are not
buffered** by the dev proxy — tokens appear one-by-one in the UI. The backend
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
