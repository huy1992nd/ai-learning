# TC-HOME-SYM-H02 - Submit valid symptoms and receive triage response

## Mục tiêu

Kiểm tra người dùng nhập triệu chứng hợp lệ sau khi chọn `Mô tả triệu chứng` và nhận phản hồi phân loại/tư vấn từ bot.

## Preconditions

- Hoàn thành `TC-HOME-SYM-H01`.
- Backend `/api/chat/stream` hoạt động và stream được SSE.

## Steps

1. Click vào textarea trong chatbot.
2. Nhập mô tả triệu chứng.
3. Click nút `send`.
4. Chờ bot trả lời xong.

## Input values

```text
Tôi bị đau ngực âm ỉ, khó thở khi đi bộ nhanh và mệt mỏi từ hôm qua. Tôi 35 tuổi, nam, muốn được tư vấn khoa khám phù hợp.
```

## Expected results

- User bubble hiển thị đúng nội dung đã nhập.
- Request gửi tới `POST http://localhost:8000/api/chat/stream`.
- Request body có `session_id` hiện tại và `message` đã nhập.
- Bot trả lời bằng tiếng Việt.
- Phản hồi rõ ràng về khoa khám đề xuất hoặc một câu làm rõ ngắn (ưu tiên phân luồng khoa), không chỉ tư vấn chung chung hoặc không khớp triệu chứng.
- Nếu backend emit card `disease` hoặc `department`, UI render card tương ứng.
- Textarea được clear sau khi gửi.
- Send button disabled khi textarea rỗng.
