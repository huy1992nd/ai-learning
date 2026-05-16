# TC-HOME-SYM-E02 - Double click quick prompt does not create duplicate active stream

## Mục tiêu

Kiểm tra double click `Mô tả triệu chứng` không tạo nhiều message hoặc nhiều stream trùng nhau.

## Preconditions

- Frontend và backend đang chạy.
- Chat widget đang mở.
- Chat session mới, quick prompt chips đang hiển thị.

## Steps

1. Double click nhanh vào `Mô tả triệu chứng`.
2. Quan sát message list trong lúc bot streaming.

## Input values

| Step | Input |
| --- | --- |
| 1 | Double click chip `Mô tả triệu chứng` |

## Expected results

- Tối đa một user bubble `Tôi có một số triệu chứng muốn mô tả`.
- Tối đa một assistant response active.
- Quick prompt chips biến mất sau click hợp lệ đầu tiên.
- Input disabled trong lúc streaming.
- Không gửi duplicate request `/api/chat/stream` cho cùng prompt.
