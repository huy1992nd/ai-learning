# TC-HOME-SYM-H03 - Accept booking and open registration form

## Mục tiêu

Kiểm tra luồng đặt lịch sau khi bot đã tư vấn triệu chứng và người dùng đồng ý đặt lịch khám.

## Preconditions

- Hoàn thành `TC-HOME-SYM-H02`.
- Backend resolve được department (embedding hoặc fallback keyword khi embedding lỗi).
- Backend có thể emit SSE `event: appointment` với `appointmentSetupDone: true`.

## Steps

1. Sau khi bot đã nêu khoa phù hợp, bot phải hỏi ngắn gọn có muốn đặt lịch khám trước tại khoa đó không (template deterministic); nhập xác nhận đặt lịch.
2. Nếu bot hỏi thông tin cá nhân, nhập đầy đủ thông tin.
3. Chờ bot trả lời xong.
4. Click `Nhấn để vào form đăng ký`.

## Input values

| Step | Input |
| --- | --- |
| 1 | `Có, tôi muốn đặt lịch khám sớm.` |
| 2 | `Họ tên Nguyễn Văn A, nam, sinh ngày 01/01/1990, số điện thoại 0901234567, email vana@example.com, địa chỉ Hà Nội.` |

## Expected results

- User bubble hiển thị tin nhắn xác nhận đặt lịch.
- Lượt hỏi đặt lịch dùng câu cố định có nhắc đúng tên khoa và hỏi có/không (không chỉ là đoạn tư vấn tự do).
- Nếu thiếu thông tin, bot chỉ hỏi các trường còn thiếu.
- Khi đủ điều kiện tối thiểu, frontend nhận SSE `event: appointment`.
- Sau khi đủ thông tin tối thiểu, bot có thể trả lời ngắn đề nghị bấm nút mở form (thông điệp deterministic); không khẳng định “không thể đặt lịch trực tiếp” trong luồng nội bộ.
- Button `Nhấn để vào form đăng ký` hiển thị đúng một lần.
- Click button điều hướng tới `/appointment/register?sessionId=<current-session-id>`.
- Form đăng ký khám hiển thị.
- Các thông tin draft từ chat được prefill nếu backend trả về dữ liệu.
