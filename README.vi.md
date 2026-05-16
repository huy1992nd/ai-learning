# MedAssist - Tóm tắt thay đổi chức năng

Tài liệu này tóm tắt các thay đổi chính ở Workshop 04. Mục tiêu là giúp người đọc nắm nhanh chức năng mới, phạm vi backend/frontend, các quyết định kiến trúc và lý do lựa chọn.

> **Lưu ý về dữ liệu test Knowledge Base:** các test case / tài liệu Knowledge Base mẫu đã được nén trong file [`docs/knowledge_base.zip`](docs/knowledge_base.zip). Khi cần kiểm thử lại luồng import/upload dữ liệu KB, giải nén file này trong môi trường local thay vì commit trực tiếp toàn bộ thư mục dữ liệu sinh ra.

## Tổng quan chức năng mới

Phiên bản này mở rộng MedAssist theo 3 hướng chính:

1. **Knowledge Base & RAG Q&A**: thêm hệ thống quản lý tài liệu y tế, ingest nội dung, tạo embedding, lưu vector và trả lời câu hỏi dựa trên Knowledge Base.
2. **Cải thiện chat triage và booking**: bổ sung đồng bộ ngôn ngữ UI với backend, fallback phân khoa bằng keyword khi embedding chưa đủ chắc chắn, và cải thiện luồng hỏi triệu chứng - gợi ý đặt lịch.
3. **Tài liệu test UI**: thêm bộ test case dạng markdown cho các luồng Home Chat, mô tả triệu chứng và tra cứu bệnh.

## Knowledge Base & RAG

Backend bổ sung một cụm API riêng cho Knowledge Base, tách biệt với luồng MedAssist chat chính:

- `POST /api/knowledge/chat/stream`: chat SSE dùng RAG để hỏi đáp từ Knowledge Base.
- `GET /api/admin/knowledge-base/documents`: danh sách tài liệu KB có phân trang.
- `POST /api/admin/knowledge-base/documents`: upload file hoặc tạo tài liệu inline text.
- `PATCH /api/admin/knowledge-base/documents/{id}`: cập nhật metadata.
- `DELETE /api/admin/knowledge-base/documents/{id}`: soft-delete tài liệu và xóa vector tương ứng.
- `POST /api/admin/knowledge-base/documents/{id}/retry`: chạy lại ingest cho tài liệu lỗi.
- `POST /api/admin/knowledge-base/documents/bulk-upload`: upload nhiều file cùng category.
- `POST /api/admin/knowledge-base/import-json`: import tài liệu dạng JSON.
- `GET /api/admin/vector-store/stats`: xem thống kê vector store.
- `POST /api/admin/vector-store/search`: test truy vấn vector thủ công.
- `POST /api/admin/vector-store/rebuild`: rebuild lại collection từ tài liệu active.
- `GET /api/admin/analytics/rag-queries`: xem log câu hỏi RAG.
- `GET /api/admin/analytics/knowledge-gaps`: xem các truy vấn chưa retrieve được context tốt.

Luồng xử lý tài liệu mới:

1. Admin upload file, bulk upload, import JSON hoặc nhập nội dung inline.
2. Backend lưu metadata vào SQLite.
3. FastAPI `BackgroundTasks` chạy ingest.
4. Ingest trích xuất text, chia chunk, gọi embedding API.
5. Chunk được lưu vào SQLite, vector được upsert vào Chroma.
6. RAG chat retrieve chunk phù hợp, dựng context và stream câu trả lời bằng SSE.

## Admin UI Knowledge Base

Frontend admin được mở rộng để reviewer/admin thao tác với Knowledge Base:

- Danh sách tài liệu có trạng thái xử lý, category, số chunk và ngày upload.
- Phân trang server-side để không tải toàn bộ dữ liệu một lần.
- Upload dialog hỗ trợ quy trình nhập tài liệu KB.
- Hiển thị lỗi rõ hơn khi không tải được danh sách hoặc upload thất bại.

Các model và service Angular tương ứng được cập nhật ở nhóm `knowledge-base.models.ts` và `admin-kb-api.service.ts`.

## Chat người dùng

Widget chat ở trang Home có hai chế độ rõ ràng hơn:

- **Mô tả triệu chứng**: đi qua luồng MedAssist chính `/api/chat/stream`, gồm guard chủ đề, triage, phân khoa và booking.
- **Tra cứu bệnh**: chuyển sang Knowledge Research Mode và gọi `/api/knowledge/chat/stream`, chỉ trả lời dựa trên Knowledge Base.

Luồng chat MedAssist chính hiện gửi thêm `language` từ `I18nService.locale()` trong payload. Việc này giúp backend dùng đúng ngôn ngữ UI cho các template xác định, đặc biệt trong các lượt trả lời ngắn như `yes`, `no`, `ok`, hoặc khi nội dung người dùng không đủ tín hiệu để detect ngôn ngữ ổn định.

## Cải thiện triage và booking

Backend chat pipeline được cải thiện ở các điểm:

- Thêm `pipeline_language.py` để resolve ngôn ngữ theo thứ tự ưu tiên: locale client gửi lên, cache session, heuristic/script, rồi langdetect.
- Bổ sung template đa ngôn ngữ cho các câu trả lời xác định trong guard, PII, triage và booking.
- Thêm `department_keyword_triage.py` để fallback phân khoa bằng keyword khi embedding không được cấu hình hoặc kết quả chưa đủ tin cậy.
- Thêm logic nhận diện tình huống cấp cứu theo keyword để ưu tiên khoa cấp cứu nếu DB có khoa tương ứng.
- Điều chỉnh booking flow để gợi ý form đăng ký lịch rõ hơn khi đã đủ điều kiện.

## Quyết định kiến trúc đáng chú ý

### Tách RAG khỏi MedAssist chat chính

RAG được triển khai ở endpoint riêng `/api/knowledge/chat/stream`, không gộp vào `/api/chat/stream`.

Lý do:

- Tránh làm nhiễu luồng UC-00 đến UC-12 vốn phục vụ triage, thu thập thông tin và đặt lịch.
- Cho phép RAG chỉ trả lời theo tài liệu tham khảo, không tự chẩn đoán, không đặt lịch và không ghi đè state y tế của session chính.
- Giữ contract SSE tương tự chat chính để frontend tái sử dụng cơ chế stream token.

### Lưu metadata trong SQLite, vector trong Chroma

SQLite tiếp tục là nguồn dữ liệu demo chính cho tài liệu, chunk, trạng thái ingest và log truy vấn. Chroma chỉ lưu vector và metadata tối thiểu để phục vụ search.

Lý do:

- SQLite phù hợp với cấu trúc hiện có của project và dễ inspect khi demo.
- Chroma đảm nhiệm phần vector search, không ép backend tự quản lý cosine search thủ công.
- Việc tách metadata và vector giúp soft-delete, retry ingest và rebuild collection rõ ràng hơn.

### Ingest chạy nền bằng FastAPI BackgroundTasks

API upload/import trả về `202 Accepted`, sau đó xử lý extract, chunk, embed và upsert vector trong background task.

Lý do:

- Upload tài liệu không bị block bởi embedding API.
- Admin có thể xem trạng thái `pending`, `processing`, `completed`, `failed`.
- Khi embedding API lỗi, hệ thống lưu lỗi ngắn gọn cho UI và vẫn giữ log chi tiết ở backend.

### Fallback keyword triage bên cạnh embedding

Phân khoa không chỉ dựa vào embedding. Khi embedding không có hoặc kết quả mơ hồ, backend dùng scoring keyword từ catalog khoa.

Lý do:

- Demo vẫn chạy được khi chưa cấu hình embedding.
- Các triệu chứng phổ biến bằng tiếng Việt/Anh có thể được map ổn định hơn.
- Quy tắc emergency override giúp không bỏ lỡ những cụm từ cấp cứu rõ ràng.

### Đồng bộ ngôn ngữ từ UI xuống backend

Frontend gửi locale đang chọn vào `/chat/stream`; backend ưu tiên giá trị này trước cache/detect.

Lý do:

- UI language là tín hiệu deterministic hơn so với detect từ câu ngắn.
- Các template như hỏi PII, xác nhận booking, từ chối ngoài y tế cần nhất quán với ngôn ngữ người dùng đang chọn.
- Giảm lỗi trả lời mặc định tiếng Việt khi người dùng đang dùng UI tiếng Anh/Nhật.

## Test và tài liệu kiểm thử

Backend có thêm test tập trung cho:

- Resolve ngôn ngữ pipeline.
- Triage và booking flow.
- Keyword-based triage trong các tình huống cần fallback.

Frontend/test documentation có thêm các test case markdown dưới:

- `docs/testcases/home/symptom-description/`
- `docs/testcases/home/disease-research/`

Các nhóm test bao phủ happy path và edge case như backend unavailable, double click prompt, empty input, stop streaming, no department match, reset conversation và follow-up trong research mode.

## Ghi chú vận hành

- Cấu hình Knowledge Base/RAG nằm trong `.env` thông qua các biến như `KB_COLLECTION_NAME`, `RAG_RETRIEVAL_TOP_K`, `RAG_SIMILARITY_MAX_DISTANCE`, `KB_MAX_UPLOAD_MB`, `RAG_CHUNK_TARGET_TOKENS`, `RAG_CHUNK_OVERLAP_TOKENS`, `CHROMA_PERSIST_DIR` và nhóm biến embedding OpenAI/Azure OpenAI.
- Thư mục con sinh bởi Chroma trong `src/api/dummy/chroma_store/` được ignore bằng `.gitignore` để tránh commit dữ liệu vector local.
- File `docs/knowledge_base.zip` là nguồn dữ liệu test KB đã nén cho reviewer.

## Lệnh verify đã dùng

```bash
npm run build
python -m pytest src/api/tests/test_pipeline_language.py src/api/tests/test_triage_booking.py
```

## PIC Group 4 Doraemon

| Account | Vai trò & góp phần |
|----|--------------------|
| ThongHM4 | Product Owner, Refinements, Reviewer, QC |
| HienT4 | BA, Documentation, Technical Writer, Testcases |
| HuyNQ298 | Backend Developer, Technical implement |
| DienNV9 | Frontend Developer |
| AnhDV61 | Frontend Developer |
