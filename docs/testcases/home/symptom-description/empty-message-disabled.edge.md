# TC-HOME-SYM-E01 - Empty and whitespace-only message cannot be sent

## Mục tiêu

Kiểm tra textarea không cho gửi message rỗng hoặc chỉ có khoảng trắng trong luồng mô tả triệu chứng.

## Preconditions

- Frontend chạy tại `http://localhost:4200`.
- Chat widget đang mở.
- Chat session mới.

## Steps

1. Không click quick prompt.
2. Nhập khoảng trắng vào textarea.
3. Thử click `send`.
4. Nhấn `Enter`.

## Input values

```text
   
```

## Expected results

- Send button vẫn disabled.
- Không có user bubble mới.
- Không gọi `/api/chat/stream`.
- Textarea vẫn editable.
- Không hiển thị error.
