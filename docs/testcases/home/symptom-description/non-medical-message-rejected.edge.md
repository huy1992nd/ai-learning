# TC-HOME-SYM-E05 - Non-medical message after symptom prompt is rejected or redirected

## Mục tiêu

Kiểm tra bot không trả lời nội dung ngoài y tế khi người dùng nhập request không liên quan sau prompt mô tả triệu chứng.

## Preconditions

- Frontend và backend đang chạy.
- Đã click `Mô tả triệu chứng`.
- Bot đã hỏi người dùng mô tả triệu chứng.

## Steps

1. Nhập request không liên quan đến y tế.
2. Click `send`.
3. Chờ bot trả lời xong.

## Input values

```text
Hãy viết cho tôi một bài quảng cáo bán điện thoại.
```

## Expected results

- User bubble hiển thị đúng input.
- Bot không tạo nội dung marketing bán điện thoại.
- Bot giải thích phạm vi hỗ trợ là sức khỏe, triệu chứng, tư vấn y tế hoặc đặt lịch khám.
- Conversation vẫn recover được để người dùng nhập triệu chứng y tế sau đó, trừ khi backend chủ động đóng thread.
