# TC-HOME-RES-H03 - Continue research in the same knowledge mode

## Mục tiêu

Kiểm tra câu hỏi tiếp theo vẫn dùng context nghiên cứu bệnh lý và vẫn gọi endpoint knowledge chat.

## Preconditions

- Hoàn thành `TC-HOME-RES-H02`.
- Bot đã trả lời về bệnh `Tăng huyết áp`.

## Steps

1. Nhập câu hỏi follow-up về bệnh vừa nghiên cứu.
2. Click `send`.
3. Chờ bot trả lời xong.

## Input values

```text
Bệnh này có dấu hiệu nguy hiểm nào cần đi khám ngay?
```

## Expected results

- User bubble hiển thị câu hỏi follow-up.
- Request tiếp tục gửi tới `/api/knowledge/chat/stream`.
- Bot giữ context bệnh đã hỏi trước đó.
- Bot trả lời theo hướng knowledge-base/medical research.
- Bot không tự chuyển sang symptom booking flow nếu người dùng chưa yêu cầu đặt lịch.
