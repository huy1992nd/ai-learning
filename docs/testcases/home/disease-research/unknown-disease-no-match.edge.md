# TC-HOME-RES-E02 - Unknown disease or no matching knowledge document

## Mục tiêu

Kiểm tra bot xử lý tên bệnh không có trong knowledge base mà không bịa thông tin.

## Preconditions

- Frontend và backend đang chạy.
- Đã click `Nghiên cứu bệnh lý`.
- Knowledge base không có tài liệu phù hợp cho input test.

## Steps

1. Nhập tên bệnh không tồn tại hoặc không được hỗ trợ.
2. Click `send`.
3. Chờ bot trả lời xong.

## Input values

```text
Bệnh không tồn tại ABCXYZ 999
```

## Expected results

- User bubble hiển thị đúng tên bệnh đã nhập.
- Request gửi tới `/api/knowledge/chat/stream`.
- Bot nói rõ không tìm thấy thông tin phù hợp hoặc yêu cầu người dùng làm rõ tên bệnh.
- Bot không trả lời chắc chắn như thể knowledge base có bệnh này.
- Textarea enable lại sau streaming.
- Người dùng có thể nhập tên bệnh khác mà không cần tạo hội thoại mới.
