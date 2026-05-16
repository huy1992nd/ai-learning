# TC-HOME-SYM-E03 - Backend unavailable shows friendly inline error

## Mục tiêu

Kiểm tra UI hiển thị lỗi thân thiện khi backend không khả dụng trong lúc bắt đầu luồng mô tả triệu chứng.

## Preconditions

- Frontend chạy tại `http://localhost:4200`.
- Backend `localhost:8000` bị stop hoặc không truy cập được.
- Chat session mới.

## Steps

1. Mở chat widget.
2. Click `Mô tả triệu chứng`.
3. Chờ request fail.

## Input values

| Step | Input |
| --- | --- |
| 2 | Click chip `Mô tả triệu chứng` |

## Expected results

- User bubble vẫn hiển thị `Tôi có một số triệu chứng muốn mô tả`.
- Assistant placeholder được thay bằng error message thân thiện.
- Streaming state được clear sau khi fail.
- Textarea usable lại theo trạng thái conversation hiện tại.
- Không hiển thị raw stack trace hoặc lỗi kỹ thuật chưa dịch.
