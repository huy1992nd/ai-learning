# TC-HOME-RES-E04 - Stop disease research streaming response

## Mục tiêu

Kiểm tra người dùng có thể dừng phản hồi đang stream trong luồng nghiên cứu bệnh lý.

## Preconditions

- Frontend và backend đang chạy.
- Đã click `Nghiên cứu bệnh lý`.
- Backend trả lời đủ chậm để thấy trạng thái streaming.

## Steps

1. Nhập tên bệnh có trong knowledge base.
2. Click `send`.
3. Khi bot đang streaming, click stop.

## Input values

```text
Đái tháo đường
```

## Expected results

- Request gửi tới `/api/knowledge/chat/stream`.
- Stop button chỉ hiển thị trong lúc streaming.
- Click stop abort active fetch request.
- Nếu assistant text còn rỗng, placeholder bị remove.
- Nếu đã có partial text, partial text vẫn hiển thị.
- Textarea enable lại sau abort.
- Câu hỏi research hợp lệ tiếp theo vẫn gửi tới `/api/knowledge/chat/stream`.
