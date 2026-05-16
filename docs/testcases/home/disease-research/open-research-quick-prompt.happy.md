# TC-HOME-RES-H01 - Open disease research mode from quick prompt

## Mục tiêu

Kiểm tra người dùng bắt đầu luồng `Nghiên cứu bệnh lý` từ quick prompt trên trang chủ.

## Preconditions

- Frontend chạy tại `http://localhost:4200`.
- Locale là Vietnamese.
- Chat session mới.

## Steps

1. Mở `http://localhost:4200`.
2. Click nút nổi `smart_toy` để mở chatbot.
3. Click `Nghiên cứu bệnh lý`.

## Input values

| Step | Input |
| --- | --- |
| 3 | Click chip `Nghiên cứu bệnh lý` |

## Expected results

- Chat widget vẫn mở.
- Quick prompt chips biến mất.
- Không tạo user bubble cho quick prompt.
- Assistant message hiển thị: `Chắc chắn rồi, bạn muốn tìm hiểu về bệnh nào?...`
- Frontend bật knowledge research mode cho message tiếp theo.
- Không gọi API ngay tại thời điểm click quick prompt.
- Textarea vẫn enabled để nhập tên bệnh.
