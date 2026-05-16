# TC-HOME-SYM-E04 - User stops a long streaming response

## Mục tiêu

Kiểm tra người dùng có thể dừng phản hồi đang stream trong luồng mô tả triệu chứng.

## Preconditions

- Frontend và backend đang chạy.
- Chat widget đang mở.
- Backend trả lời đủ chậm để thấy trạng thái streaming.

## Steps

1. Click `Mô tả triệu chứng`.
2. Khi bot đang streaming, click nút stop.

## Input values

| Step | Input |
| --- | --- |
| 1 | Click chip `Mô tả triệu chứng` |
| 2 | Click stop icon |

## Expected results

- Fetch request bị abort.
- Nếu assistant placeholder còn rỗng, placeholder bị remove.
- Nếu đã có partial text, partial text vẫn hiển thị.
- Streaming state được clear.
- Textarea enable lại.
- User có thể gửi message tiếp theo.
