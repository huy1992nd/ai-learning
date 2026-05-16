# TC-HOME-RES-E05 - Switching from research to symptom flow requires new conversation

## Mục tiêu

Kiểm tra sau khi vào research mode, message tiếp theo vẫn dùng endpoint knowledge cho đến khi người dùng tạo hội thoại mới.

## Preconditions

- Frontend và backend đang chạy.
- Chat session mới.

## Steps

1. Click `Nghiên cứu bệnh lý`.
2. Nhập tên bệnh hợp lệ và chờ bot trả lời.
3. Nhập một message giống mô tả triệu chứng mà không click `add_comment`.
4. Quan sát endpoint được gọi.
5. Click `add_comment`.
6. Click `Mô tả triệu chứng`.

## Input values

| Step | Input |
| --- | --- |
| 2 | `Tăng huyết áp` |
| 3 | `Tôi bị đau đầu và chóng mặt, tôi muốn đặt lịch khám.` |
| 6 | Click chip `Mô tả triệu chứng` |

## Expected results

- Step 3 vẫn gọi `/api/knowledge/chat/stream` vì research mode còn active.
- Bot trả lời theo hướng research hoặc hướng dẫn tạo hội thoại triệu chứng mới.
- Không hiển thị booking CTA nếu backend không hỗ trợ transition này.
- Sau khi click `add_comment`, messages bị clear và research mode reset.
- Step 6 gọi `/api/chat/stream`.
