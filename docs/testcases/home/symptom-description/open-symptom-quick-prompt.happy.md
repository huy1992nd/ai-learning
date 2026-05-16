# TC-HOME-SYM-H01 - Open symptom flow from quick prompt

## Mục tiêu

Kiểm tra người dùng mở chatbot từ trang chủ và bắt đầu luồng `Mô tả triệu chứng` bằng quick prompt.

## Preconditions

- Frontend chạy tại `http://localhost:4200`.
- Backend chạy tại `http://localhost:8000`.
- Locale là Vietnamese.
- Chat session mới, chưa có message.

## Steps

1. Mở `http://localhost:4200`.
2. Click nút nổi `smart_toy` để mở chatbot.
3. Xác nhận welcome message hiển thị.
4. Click `Mô tả triệu chứng`.

## Input values

| Step | Input |
| --- | --- |
| 4 | Click chip `Mô tả triệu chứng` |

## Expected results

- Chat widget vẫn mở.
- Quick prompt chips biến mất sau khi click.
- User bubble hiển thị `Tôi có một số triệu chứng muốn mô tả`.
- Frontend gọi `POST /api/chat/stream`.
- Input bị disabled trong lúc streaming.
- Sau khi streaming xong, textarea được enable lại.
- Không tạo duplicate user message.
