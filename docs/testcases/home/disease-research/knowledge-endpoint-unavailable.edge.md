# TC-HOME-RES-E03 - Backend knowledge endpoint unavailable

## Mục tiêu

Kiểm tra UI hiển thị lỗi thân thiện khi endpoint knowledge chat không khả dụng.

## Preconditions

- Frontend chạy tại `http://localhost:4200`.
- Backend route `/api/knowledge/chat/stream` bị stop, lỗi hoặc không truy cập được.
- Đã click `Nghiên cứu bệnh lý`.

## Steps

1. Nhập tên bệnh.
2. Click `send`.
3. Chờ request fail.

## Input values

```text
Hen suyễn
```

## Expected results

- Research greeting vẫn hiển thị trước khi gửi.
- User bubble hiển thị `Hen suyễn`.
- Assistant placeholder được thay bằng error message thân thiện.
- Không hiển thị raw stack trace, HTTP dump hoặc exception chưa dịch.
- Streaming state được clear.
- Textarea enable lại.
- Research mode vẫn active để retry vẫn gọi `/api/knowledge/chat/stream`.
