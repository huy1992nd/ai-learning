# Hướng dẫn cho AI agents (MedAssist / workshop-03)

## Đọc kiến trúc trước khi sửa code

Trước khi phân tích, thiết kế hoặc chỉnh sửa mã nguồn, hãy **đọc đúng** tài liệu kiến trúc theo phạm vi công việc:

| Loại task | Tài liệu bắt buộc đọc |
| --- | --- |
| Backend (Python, FastAPI, SQLite, pipeline chat, API, audio, admin API…) | [`.agents/architecture/BACKEND.md`](.agents/architecture/BACKEND.md) |
| Frontend (Angular, UI, i18n, chat widget, form đặt lịch, admin portal…) | [`.agents/architecture/FRONTEND.md`](.agents/architecture/FRONTEND.md) |
| Full-stack, luồng end-to-end (chat → session → form → API), hoặc thay đổi contract API/UI | Đọc **cả hai** file trên |

## Tài liệu tổng hợp (tuỳ chọn)

[`.agents/architecture.md`](.agents/architecture.md) là bản gộp dài hơn (kiến trúc chung + chi tiết). Có thể tham khảo khi cần ngữ cảnh rộng; khi đã đọc `BACKEND.md` / `FRONTEND.md` thì không bắt buộc lặp lại toàn bộ file gộp.

## Ghi nhớ ngắn

- Backend nằm dưới `src/api/`, frontend dưới `src/webui/`.
- Các router HTTP backend mount tại prefix `/api` (xem `src/api/app/main.py` và file map trong `BACKEND.md`).

## Quy ước tạo plan

Khi được yêu cầu tạo plan, luôn lưu plan trong thư mục [`.agents/plans`](.agents/plans) với quy ước đặt tên:

```text
<timestamp>-<name-plan>.md
```

Trong đó `<timestamp>` nên dùng định dạng dễ sắp xếp theo thời gian, ví dụ `YYYYMMDD-HHMMSS`, và `<name-plan>` là tên ngắn gọn dạng kebab-case.
