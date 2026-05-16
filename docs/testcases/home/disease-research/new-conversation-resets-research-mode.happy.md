# TC-HOME-RES-H04 - New conversation resets research mode

## Mục tiêu

Kiểm tra nút tạo hội thoại mới reset research mode để người dùng có thể chuyển lại sang luồng mô tả triệu chứng.

## Preconditions

- Hoàn thành `TC-HOME-RES-H02`.
- Chat đang ở knowledge research mode.

## Steps

1. Click `add_comment`.
2. Xác nhận messages cũ đã bị clear.
3. Click `Mô tả triệu chứng`.

## Input values

| Step | Input |
| --- | --- |
| 1 | Click `add_comment` |
| 3 | Click chip `Mô tả triệu chứng` |

## Expected results

- Messages cũ bị clear.
- Session id mới được tạo.
- Quick prompt chips hiển thị lại.
- Knowledge research mode được reset.
- Click `Mô tả triệu chứng` gọi `/api/chat/stream`, không gọi `/api/knowledge/chat/stream`.
