# TC-HOME-RES-E01 - Empty disease name cannot be sent

## Mục tiêu

Kiểm tra không thể gửi tên bệnh rỗng hoặc chỉ có khoảng trắng trong luồng nghiên cứu bệnh lý.

## Preconditions

- Frontend chạy tại `http://localhost:4200`.
- Đã click `Nghiên cứu bệnh lý`.
- Research greeting đang hiển thị.

## Steps

1. Nhập whitespace vào textarea.
2. Thử click `send`.
3. Nhấn `Enter`.

## Input values

```text
   
```

## Expected results

- Send button vẫn disabled.
- Không thêm user bubble.
- Không gọi `/api/knowledge/chat/stream`.
- Research mode vẫn active cho input hợp lệ tiếp theo.
