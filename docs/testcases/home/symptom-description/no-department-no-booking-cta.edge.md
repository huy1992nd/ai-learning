# TC-HOME-SYM-E06 - Booking CTA is not shown when backend cannot resolve department

## Mục tiêu

Kiểm tra frontend không tự hiển thị CTA đặt lịch khi backend không resolve được khoa hoặc không emit appointment event.

## Preconditions

- Frontend và backend đang chạy.
- Backend được cấu hình sao cho department triage không resolve được department, hoặc embedding model/API key bị lỗi.
- Chat session mới.

## Steps

1. Click `Mô tả triệu chứng`.
2. Nhập triệu chứng hợp lệ.
3. Nhập xác nhận muốn đặt lịch.
4. Quan sát message list và CTA.

## Input values

| Step | Input |
| --- | --- |
| 2 | `Tôi bị đau ngực âm ỉ, khó thở khi đi bộ nhanh, mệt mỏi từ hôm qua.` |
| 3 | `Có, tôi muốn đặt lịch khám.` |

## Expected results

- Bot có thể vẫn đưa ra tư vấn chung.
- Button `Nhấn để vào form đăng ký` không xuất hiện nếu không có SSE `event: appointment`.
- Frontend không tự điều hướng tới `/appointment/register`.
- Chat UI không bị crash.
- Đây là lỗi backend/config nếu kỳ vọng sản phẩm là đặt lịch thành công.
