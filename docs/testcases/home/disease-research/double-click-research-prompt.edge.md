# TC-HOME-RES-E06 - Double click research quick prompt

## Mục tiêu

Kiểm tra double click `Nghiên cứu bệnh lý` không seed nhiều greeting hoặc gây trạng thái research mode bất thường.

## Preconditions

- Frontend chạy tại `http://localhost:4200`.
- Chat widget đang mở.
- Chat session mới, quick prompt chips đang hiển thị.

## Steps

1. Double click nhanh vào `Nghiên cứu bệnh lý`.
2. Quan sát message list và textarea.

## Input values

| Step | Input |
| --- | --- |
| 1 | Double click chip `Nghiên cứu bệnh lý` |

## Expected results

- Tối đa một research greeting được seed.
- Quick prompt chips biến mất sau click hợp lệ đầu tiên.
- Không gọi API ngay.
- Textarea vẫn enabled để nhập tên bệnh.
- Knowledge research mode active.
