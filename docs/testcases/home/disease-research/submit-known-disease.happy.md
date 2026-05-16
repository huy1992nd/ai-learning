# TC-HOME-RES-H02 - Submit known disease name and receive knowledge-base answer

## Mục tiêu

Kiểm tra người dùng nhập tên bệnh có trong knowledge base và nhận câu trả lời từ luồng RAG.

## Preconditions

- Hoàn thành `TC-HOME-RES-H01`.
- Backend `/api/knowledge/chat/stream` hoạt động.
- Knowledge base có tài liệu active/indexed cho bệnh được test.

## Steps

1. Nhập tên bệnh vào textarea.
2. Click `send`.
3. Chờ bot trả lời xong.

## Input values

```text
Tăng huyết áp
```

## Expected results

- User bubble hiển thị `Tăng huyết áp`.
- Request gửi tới `POST http://localhost:8000/api/knowledge/chat/stream`.
- Request không gửi tới `/api/chat/stream`.
- Request body có `session_id` hiện tại và `message`.
- Bot trả lời bằng tiếng Việt.
- Bot tóm tắt thông tin bệnh từ knowledge base.
- Response có thông tin hữu ích như tổng quan, triệu chứng, nguy cơ, phòng ngừa hoặc khi nào cần đi khám.
- Textarea được clear sau khi gửi.
- Không hiển thị CTA đăng ký khám cho luồng research thuần túy nếu backend không emit appointment event.
