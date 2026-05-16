MedAssist AI — Software Requirements Specification (SRS)
Chuẩn tham chiếu: IEEE 830 / ISO/IEC 29148
Version: 1.0  
Date: 2026-04-18  
Author: HienT4 / BA / Tech Team

MedAssist AI — Software Requirements Specification (SRS) 1
MỤC LỤC 1

1. Giới thiệu 1
   1.1 Mục đích tài liệu 2
   1.2 Phạm vi tài liệu 2
   1.3 Định nghĩa và từ viết tắt 2
   1.4 Tài liệu tham chiếu 3
2. Mô tả tổng quan hệ thống 3
   2.1 Bối cảnh sản phẩm 3
   2.2 Kiến trúc tổng thể 3
   2.3 Luồng hội thoại tổng quát 3
3. Các bên liên quan và người dùng 4
   3.1 Stakeholders 4
   3.2 Actors kỹ thuật 4
   3.3 Đặc điểm người dùng 4
4. Yêu cầu chức năng (Functional Requirements) 4
   4.1 UC-00: Kiểm soát chủ đề hội thoại (Topic Guard) 4
   4.2 UC-01: Phát hiện ngôn ngữ & Phản hồi đa ngôn ngữ 5
   4.3 UC-02: Khai báo triệu chứng 5
   4.4 UC-03: Dự đoán bệnh (Disease Prediction) 6
   4.5 UC-04: Gợi ý Khoa & Bác sĩ 6
   4.6 UC-05: Thu thập thông tin bệnh nhân (Auto Form Fill) 7
   4.7 UC-06: Kiểm tra lịch trống của bác sĩ 7
   4.8 UC-07: Gợi ý bác sĩ thay thế 7
   4.9 UC-08: Đặt lịch khám (Book Appointment) 8
   4.10 UC-09 → UC-11: Quản lý Admin & Doctor Portal 8
   4.11 Session Management 8
5. Yêu cầu phi chức năng (Non-Functional Requirements) 9
   5.1 Hiệu năng (Performance) 9
   5.2 Bảo mật (Security) 9
   5.3 Độ tin cậy (Reliability) 9
   5.4 Khả năng sử dụng (Usability) 9
   5.5 Khả năng bảo trì (Maintainability) 10
6. Yêu cầu giao diện ngoài (External Interface Requirements) 10
   6.1 Giao diện người dùng (UI) 10
   6.2 Giao diện phần mềm (Software Interface) 10
   6.3 API Endpoints chính 10
   Chat 10
   Departments & Doctors 10
   Appointments 11
   Auth 11
7. Quy tắc nghiệp vụ (Business Rules) 11
8. Ràng buộc hệ thống (Constraints) 12
9. Giả định và phụ thuộc (Assumptions & Dependencies) 12
   9.1 Giả định 12
   9.2 Phụ thuộc bên ngoài 12
10. Phạm vi hệ thống (Scope) 13
    10.1 Trong phạm vi V1 13
    10.2 Ngoài phạm vi V1 13
11. Mô hình dữ liệu (Data Model Summary) 13
12. Phụ lục 14
    12.1 Ma trận truy xuất yêu cầu (Traceability Matrix) 14
    12.2 Luồng Conversation State Machine 14
    12.3 Ưu tiên tính năng (Workshop 2) 15

13. Giới thiệu
    1.1 Mục đích tài liệu
    Tài liệu này định nghĩa đầy đủ các yêu cầu phần mềm cho hệ thống MedAssist AI — chatbot y tế thông minh hỗ trợ bệnh nhân từ khai báo triệu chứng đến đặt lịch khám tự động. Tài liệu là cơ sở thống nhất giữa các bên (BA, Developer, QA, Product Owner) về những gì hệ thống phải làm và không làm.
    1.2 Phạm vi tài liệu
    SRS này bao phủ toàn bộ hệ thống MedAssist AI V1, bao gồm:
    • Giao diện chatbot (Frontend Angular 21)
    • Backend API (FastAPI / Python 3.19)
    • AI Engine tích hợp LangChain + OpenAI GPT-4o
    • Cơ sở dữ liệu (SQLite)
    • Cổng quản trị (Admin & Doctor Portal)
    Phạm vi Workshop 2 tập trung vào: UC-00, UC-01, UC-02, UC-03, UC-04.
    1.3 Định nghĩa và từ viết tắt
    Thuật ngữ Định nghĩa
    SRS Software Requirements Specification
    BRD Business Requirements Document
    UC Use Case
    FR Functional Requirement (Yêu cầu chức năng)
    NFR Non-Functional Requirement (Yêu cầu phi chức năng)
    BR Business Rule (Quy tắc nghiệp vụ)
    AI Engine Thành phần AI xử lý ngôn ngữ tự nhiên, dự đoán bệnh
    Topic Guard Cơ chế kiểm soát chủ đề hội thoại, chỉ cho phép nội dung y tế
    Session Phiên làm việc của người dùng, có thời hạn 24 giờ
    Severity Mức độ nghiêm trọng bệnh lý: URGENT, MODERATE, MILD
    Slot Khung giờ khám còn trống của bác sĩ (mỗi slot = 1 giờ)
    SSE Server-Sent Events — giao thức streaming phản hồi AI
    JWT JSON Web Token — cơ chế xác thực cho Admin/Doctor
    PII Personally Identifiable Information — thông tin cá nhân nhạy cảm
    CCCD Căn cước công dân
    BHYT Bảo hiểm y tế
    1.4 Tài liệu tham chiếu
    Tài liệu Mô tả
    01_MedAssist_AI_BRD - Business Requirements Document.docx Yêu cầu nghiệp vụ cấp cao, mục tiêu kinh doanh
    02_MedAssist_AI_Functional Specification.docx Đặc tả chức năng chi tiết các Use Case
    03_MedAssist_AI_Technical_Spec.docx Kiến trúc, database schema, API, AI Engine
    04_MedAssist_AI_Test_Cases.xlsx Tập hợp các test case cho UC-00 → UC-04
    05_MedAssist_AI_BA_Document.docx Tài liệu BA tổng hợp

14. Mô tả tổng quan hệ thống
    2.1 Bối cảnh sản phẩm
    MedAssist AI giải quyết các vấn đề hiện tại trong quy trình đặt lịch khám y tế:
    Vấn đề Giải pháp
    Bệnh nhân mất ~10 phút để đặt lịch qua điện thoại Chatbot tự động hoàn thành trong < 3 phút
    Không biết khám khoa nào khi có triệu chứng AI gợi ý khoa và bác sĩ phù hợp
    Nhân viên lễ tân phải xử lý nhiều cuộc gọi thủ công Tự động hóa 100% quy trình thu thập thông tin và đặt lịch
    Lịch bác sĩ không tối ưu, trùng lịch hoặc bỏ trống Hệ thống quản lý slot thông minh theo mức độ bệnh
    2.2 Kiến trúc tổng thể
    ┌────────────────────────────────────────────────┐
    │ FRONTEND (Angular 21) │
    │ Chat UI · Appointment Form · Admin/Doctor UI │
    │ Angular Signals (State) │
    └───────────────────┬────────────────────────────┘
    │ HTTPS + SSE
    ┌───────────────────▼────────────────────────────┐
    │ BACKEND (FastAPI / Python 3.19) │
    │ Chat Router · Scheduling Router · Admin Router│
    │ ┌──────────────────────────────────────────┐ │
    │ │ AI Engine Service │ │
    │ │ LangChain → OpenAI GPT-4o │ │
    │ │ langdetect · Keyword Override │ │
    │ └──────────────────────────────────────────┘ │
    │ SQLAlchemy AsyncSession │
    └───────────────────┬────────────────────────────┘
    │
    ┌───────────────────▼────────────────────────────┐
    │ DATABASE (SQLite — WAL mode) │
    └────────────────────────────────────────────────┘
    2.3 Luồng hội thoại tổng quát
    TOPIC_GUARD → GREETING → SYMPTOM_COLLECTION → DISEASE_PREDICTION
    → DOCTOR_SELECTION → SLOT_SELECTION → INFO_COLLECTION
    → CONFIRMATION → COMPLETED
    TOPIC_GUARD là bước đầu tiên, chạy trên mọi tin nhắn trước khi vào bất kỳ stage nào.

15. Các bên liên quan và người dùng
    3.1 Stakeholders
    Bên liên quan Vai trò Kỳ vọng chính
    Bệnh nhân Người dùng cuối của chatbot Đặt lịch nhanh (< 3 phút), không cần tạo tài khoản
    Bác sĩ Người nhận lịch hẹn Nhận thông báo đúng giờ, xem thông tin bệnh nhân trước khám
    Quản trị viên (Admin) Vận hành hệ thống Quản lý danh mục khoa, bác sĩ, lịch làm việc
    Ban lãnh đạo bệnh viện Sponsor Báo cáo hiệu suất, giảm tải nhân sự lễ tân
    3.2 Actors kỹ thuật
    Actor Mô tả
    Patient Tương tác trực tiếp qua giao diện chatbot
    Doctor Nhận notification, quản lý lịch qua Doctor Portal
    Admin Quản lý toàn bộ dữ liệu hệ thống qua Admin Portal
    AI Engine Xử lý ngôn ngữ, phân tích triệu chứng, dự đoán bệnh
    3.3 Đặc điểm người dùng
    • Bệnh nhân: Không có kỹ năng kỹ thuật, có thể dùng nhiều ngôn ngữ khác nhau
    • Bác sĩ: Có kiến thức y tế, cần thông tin rõ ràng, giao diện đơn giản
    • Admin: Có kỹ năng vận hành hệ thống cơ bản

16. Yêu cầu chức năng (Functional Requirements)
    4.1 UC-00: Kiểm soát chủ đề hội thoại (Topic Guard)
    FR-00-01 — Hệ thống phải phân tích chủ đề của mọi tin nhắn đầu vào trước khi xử lý bất kỳ logic nghiệp vụ nào.
    FR-00-02 — Nếu tin nhắn liên quan đến y tế (triệu chứng, bệnh, bác sĩ, khoa, đặt lịch...) → hệ thống tiếp tục xử lý bình thường.
    FR-00-03 — Nếu tin nhắn không liên quan đến y tế → hệ thống phải phản hồi từ chối lịch sự bằng đúng ngôn ngữ của người dùng, với nội dung tương đương:
    "Xin lỗi, tôi chỉ có thể hỗ trợ các vấn đề liên quan đến sức khỏe và y tế. Bạn có muốn mô tả triệu chứng hoặc đặt lịch khám không?"
    FR-00-04 — Sau khi từ chối, session phải được giữ nguyên để người dùng tiếp tục hội thoại y tế.
    FR-00-05 — Hệ thống không được giải thích lý do kỹ thuật khi từ chối.
    Danh sách chủ đề bị từ chối (ví dụ): thời tiết, nấu ăn, du lịch, lập trình, công nghệ, tư vấn pháp lý/tài chính, giải trí, thể thao, chính trị.

4.2 UC-01: Phát hiện ngôn ngữ & Phản hồi đa ngôn ngữ
FR-01-01 — Hệ thống phải tự động phát hiện ngôn ngữ từ nội dung tin nhắn đầu vào, hỗ trợ mọi ngôn ngữ, không giới hạn.
FR-01-02 — Ngôn ngữ phát hiện phải được lưu vào session ngay sau khi detect.
FR-01-03 — Toàn bộ phản hồi trong session đó phải dùng đúng ngôn ngữ đã phát hiện.
FR-01-04 — Nếu người dùng chuyển ngôn ngữ giữa chừng, hệ thống phải tự cập nhật ngôn ngữ session và phản hồi theo ngôn ngữ mới kể từ tin nhắn tiếp theo.
FR-01-05 — Hệ thống không được yêu cầu người dùng khai báo ngôn ngữ thủ công.
Postcondition: Session có thuộc tính language được gán chính xác.

4.3 UC-02: Khai báo triệu chứng
FR-02-01 — Chatbot phải hỏi dẫn dắt mở đầu: "Bạn đang gặp phải triệu chứng gì?" (bằng ngôn ngữ session).
FR-02-02 — Hệ thống phải chấp nhận mô tả triệu chứng dưới dạng ngôn ngữ tự nhiên, không yêu cầu người dùng chọn từ danh sách.
FR-02-03 — AI phải trích xuất các thực thể: bộ phận cơ thể, tính chất triệu chứng, thời gian xuất hiện, mức độ đau.
FR-02-04 — Nếu thông tin chưa đủ, chatbot được phép hỏi thêm tối đa 3 lượt câu hỏi làm rõ.
FR-02-05 — Nếu sau 3 lượt vẫn không thu thập được triệu chứng rõ ràng, hệ thống phải chuyển sang UC-04 với gợi ý khoa tổng quát (Nội tổng quát), không tiếp tục vòng lặp vô hạn.
FR-02-06 — Hệ thống phải duy trì context triệu chứng xuyên suốt multi-turn conversation, không hỏi lại thông tin đã có.
Postcondition: Có danh sách triệu chứng có cấu trúc để đưa vào UC-03.

4.4 UC-03: Dự đoán bệnh (Disease Prediction)
FR-03-01 — Hệ thống phải trả về danh sách top 3–5 bệnh có khả năng mắc phải kèm mức độ tin cậy (%).
FR-03-02 — Chỉ hiển thị các bệnh có độ tin cậy ≥ 60%.
FR-03-03 — Hệ thống phải gắn nhãn mức độ nghiêm trọng tổng thể: URGENT / MODERATE / MILD.
FR-03-04 (Business Rule Override) — Nếu triệu chứng chứa từ khóa nguy hiểm (đau ngực, khó thở, bất tỉnh, liệt, co giật...) → bắt buộc gắn `URGENT` bất kể kết quả AI.
FR-03-05 — Kết quả phải hiển thị kèm disclaimer bắt buộc: "Đây là gợi ý tham khảo, không phải chẩn đoán y tế chính thức."
FR-03-06 — Nếu không có bệnh nào đạt ≥ 60%, hệ thống phải thông báo "Không đủ thông tin để dự đoán" và quay về UC-02.
Postcondition: Session có severity được gán; sẵn sàng cho UC-04.

4.5 UC-04: Gợi ý Khoa & Bác sĩ
FR-04-01 — Hệ thống phải tra cứu mapping từ bệnh dự đoán → khoa phù hợp trong bảng disease_department_mapping.
FR-04-02 (Happy Path) — Nếu tìm được khoa phù hợp:
• Hiển thị danh sách khoa gợi ý kèm mô tả ngắn.
• Hiển thị danh sách bác sĩ của từng khoa (ảnh, tên, chức danh, chuyên môn).
• Cho phép bệnh nhân chọn khoa và/hoặc bác sĩ cụ thể.
• Nếu bệnh nhân không chọn → AI tự gợi ý bác sĩ phù hợp nhất và xác nhận với bệnh nhân.
FR-04-03 (No Department Path) — Nếu không tìm được khoa nào trong DB:
• Thông báo bằng ngôn ngữ người dùng: "Rất tiếc, bệnh viện hiện chưa có chuyên khoa phù hợp để điều trị [tên bệnh]. Bạn có thể liên hệ trực tiếp với bệnh viện để được tư vấn thêm."
• Hệ thống không được mapping sang khoa không liên quan.
• Flow kết thúc tại đây; không tiếp tục đặt lịch.
Postcondition (Happy Path): Có doctor_id và department_id được chọn.  
Postcondition (No Department): Flow kết thúc; bệnh nhân nhận thông tin liên hệ bệnh viện.

4.6 UC-05: Thu thập thông tin bệnh nhân (Auto Form Fill)
FR-05-01 — Chatbot phải thu thập thông tin bệnh nhân qua hội thoại tự nhiên, từng bước:
• Họ và tên đầy đủ (bắt buộc, ≥ 2 từ)
• Ngày sinh (dd/mm/yyyy, không là ngày tương lai)
• Giới tính
• Số điện thoại (bắt buộc, 10 chữ số, bắt đầu bằng 0)
• Email (không bắt buộc, định dạng hợp lệ)
• Số CCCD hoặc mã BHYT (không bắt buộc, CCCD = 12 chữ số)
• Địa chỉ
FR-05-02 — AI phải validate từng trường ngay khi nhận; nếu sai định dạng → thông báo và yêu cầu nhập lại.
FR-05-03 — Sau khi đủ thông tin, hệ thống phải tự động điền vào form hẹn lịch và hiển thị tóm tắt để bệnh nhân xác nhận.
Postcondition: Form hẹn lịch đầy đủ; sẵn sàng cho UC-08.

4.7 UC-06: Kiểm tra lịch trống của bác sĩ
FR-06-01 — Hệ thống phải xác định khoảng thời gian tìm kiếm theo severity:
• URGENT → trong vòng 24–48 giờ tới
• MODERATE → trong vòng 7 ngày tới
• MILD → trong vòng tối đa 30 ngày tới
FR-06-02 — Hệ thống phải truy vấn lịch và hiển thị tối đa 10 slot gần nhất còn trống.
FR-06-03 — Nếu không có slot trong khoảng thời gian → chuyển sang UC-07.
FR-06-04 (Special Case) — Nếu severity = URGENT và không có slot trong 48h → hiển thị cảnh báo: "Tình trạng của bạn cần được khám gấp. Vui lòng đến phòng cấp cứu ngay lập tức."

4.8 UC-07: Gợi ý bác sĩ thay thế
FR-07-01 — Khi bác sĩ được yêu cầu không có slot phù hợp, hệ thống bắt buộc gợi ý bác sĩ thay thế cùng khoa.
FR-07-02 — Hiển thị danh sách bác sĩ thay thế kèm slot sớm nhất của mỗi bác sĩ.
FR-07-03 — Nếu bệnh nhân chọn "Chờ bác sĩ ban đầu" → mở rộng khoảng tìm kiếm thêm 30 ngày và hiển thị slot gần nhất.

4.9 UC-08: Đặt lịch khám (Book Appointment)
FR-08-01 — Khi bệnh nhân xác nhận, hệ thống phải tạo appointment record trong DB với mã duy nhất (VD: MA-20260418-0001).
FR-08-02 — Hệ thống phải block slot 1 giờ trong lịch của bác sĩ.
FR-08-03 — Hệ thống phải gửi email xác nhận đến bệnh nhân và bác sĩ.
FR-08-04 — Hệ thống phải dùng BEGIN IMMEDIATE TRANSACTION khi ghi appointment để tránh race condition.

4.10 UC-09 → UC-11: Quản lý Admin & Doctor Portal
FR-09-01 — Admin phải đăng nhập bằng JWT (email + password).
FR-09-02 — Admin có thể tạo/sửa/xóa (soft delete) khoa, bác sĩ, lịch làm việc.
FR-10-01 — Bác sĩ có thể xem lịch khám cá nhân và block slot.
FR-10-02 — Bác sĩ có thể xem danh sách lịch hẹn theo ngày.

4.11 Session Management
FR-11-01 — Session ID phải do Frontend tạo (UUID v4) và gửi kèm mỗi request — Backend không tự sinh session ID.
FR-11-02 — Session mới → Backend tạo record với messages = [system_prompt].
FR-11-03 — Session cũ → Backend load lại messages array và append tin nhắn mới.
FR-11-04 — Session tự hết hạn sau 24 giờ; cron job dọn dẹp hàng đêm.
FR-11-05 — Hệ thống giữ 6 turn gần nhất full text; từ turn thứ 7 trở đi, các turn cũ được summarize bằng LLM.
FR-11-06 — Hard limit 20 turns/session → auto-reset và thông báo người dùng.

5. Yêu cầu phi chức năng (Non-Functional Requirements)
   5.1 Hiệu năng (Performance)
   NFR Yêu cầu
   NFR-PERF-01 Chatbot bắt đầu streaming phản hồi trong ≤ 2 giây kể từ khi nhận tin nhắn
   NFR-PERF-02 API non-AI (danh sách khoa, bác sĩ, slot) phải phản hồi trong ≤ 500ms
   NFR-PERF-03 Hệ thống hỗ trợ tối đa 50 người dùng đồng thời cho phiên bản demo
   NFR-PERF-04 Giới hạn tối đa 100 lượt gọi AI/ngày để kiểm soát chi phí
   5.2 Bảo mật (Security)
   NFR Yêu cầu
   NFR-SEC-01 Mật khẩu tài khoản Admin/Doctor phải được hash bằng bcrypt
   NFR-SEC-02 Xác thực Admin/Doctor Portal bằng JWT HS256
   NFR-SEC-03 PII (CCCD, thông tin bệnh nhân) chỉ được lưu sau khi bệnh nhân xác nhận đặt lịch
   NFR-SEC-04 Tất cả giao tiếp giữa Frontend và Backend phải qua HTTPS
   NFR-SEC-05 CCCD không được ghi log; cần encrypt nếu lưu trữ
   NFR-SEC-06 Chat session chỉ tồn tại 24 giờ; không lưu lịch sử hội thoại vĩnh viễn
   NFR-SEC-07 API Admin/Doctor phải kiểm tra role từ JWT trước khi xử lý
   5.3 Độ tin cậy (Reliability)
   NFR Yêu cầu
   NFR-REL-01 Hệ thống phải xử lý lỗi kết nối OpenAI và trả về thông báo lỗi thân thiện
   NFR-REL-02 Database phải dùng WAL mode để đảm bảo tính nhất quán đọc/ghi đồng thời
   NFR-REL-03 Thao tác đặt lịch phải dùng transaction để tránh race condition
   5.4 Khả năng sử dụng (Usability)
   NFR Yêu cầu
   NFR-USE-01 Bệnh nhân không cần tạo tài khoản để sử dụng chatbot
   NFR-USE-02 Toàn bộ quy trình từ khai báo triệu chứng đến xác nhận đặt lịch phải hoàn thành trong < 3 phút
   NFR-USE-03 Giao diện chatbot phải hỗ trợ responsive (desktop và mobile browser)
   NFR-USE-04 Phản hồi AI phải dùng ngôn ngữ tự nhiên, dễ hiểu; không dùng thuật ngữ kỹ thuật
   5.5 Khả năng bảo trì (Maintainability)
   NFR Yêu cầu
   NFR-MAINT-01 AI Engine phải được implement sau AIProvider interface để dễ swap LLM provider
   NFR-MAINT-02 DB migration quản lý bằng Alembic
   NFR-MAINT-03 Frontend state quản lý bằng Angular Signals (không dùng NgRx cho demo)

6. Yêu cầu giao diện ngoài (External Interface Requirements)
   6.1 Giao diện người dùng (UI)
   • Chat Interface: Giao diện chatbot dạng bubble chat, hỗ trợ SSE streaming (chữ xuất hiện dần)
   • Appointment Form: Form xác nhận thông tin trước khi submit
   • Admin Portal: CRUD cho khoa, bác sĩ, lịch làm việc
   • Doctor Portal: Xem lịch, block slot, xem danh sách bệnh nhân
   6.2 Giao diện phần mềm (Software Interface)
   Thành phần Giao thức / Chuẩn
   Frontend ↔ Backend HTTPS REST API + SSE (text/event-stream)
   Backend ↔ OpenAI HTTPS (OpenAI API v1) qua LangChain
   Backend ↔ Email SMTP (Gmail SMTP, port 587/465)
   Backend ↔ SQLite SQLAlchemy AsyncSession
   6.3 API Endpoints chính
   Chat
   Method Endpoint Mô tả
   POST /api/chat Gửi tin nhắn; response là SSE stream
   POST /api/chat/{session_id}/reset Reset messages array của session
   Departments & Doctors
   Method Endpoint Mô tả
   GET /api/departments Danh sách khoa
   GET /api/departments/{id}/doctors Bác sĩ theo khoa
   GET /api/doctors/{id}/available-slots Slot trống (tính on-demand)
   Appointments
   Method Endpoint Mô tả
   POST /api/appointments Tạo lịch hẹn
   GET /api/appointments/{id} Tra cứu lịch hẹn (không cần login)
   PATCH /api/appointments/{id}/cancel Huỷ lịch hẹn (JWT required)
   Auth
   Method Endpoint Mô tả
   POST /api/auth/login Đăng nhập Admin/Doctor, trả về JWT

7. Quy tắc nghiệp vụ (Business Rules)
   BR# Quy tắc
   BR-00 Chatbot chỉ trả lời các chủ đề liên quan đến y tế và sức khỏe — từ chối lịch sự mọi yêu cầu khác bằng ngôn ngữ của người dùng
   BR-01 Hệ thống chỉ được gợi ý, không được chẩn đoán — phải hiển thị disclaimer bắt buộc
   BR-02 Triệu chứng URGENT (đau ngực, khó thở, bất tỉnh...) → ưu tiên tìm lịch trong 24–48 giờ
   BR-03 Triệu chứng MODERATE → tìm lịch trong vòng 7 ngày
   BR-04 Triệu chứng MILD → tìm lịch tối đa 30 ngày
   BR-05 Nếu không có lịch URGENT trong 48h → cảnh báo bệnh nhân đến cấp cứu ngay
   BR-06 Mỗi ca khám chuẩn là 1 tiếng
   BR-07 Bệnh nhân không cần tạo tài khoản để đặt lịch
   BR-08 Thông tin cá nhân bệnh nhân chỉ lưu vĩnh viễn sau khi xác nhận đặt lịch
   BR-09 Khi bác sĩ được yêu cầu hết lịch → hệ thống bắt buộc gợi ý bác sĩ thay thế cùng khoa
   BR-10 Session ID do Frontend tạo (UUID v4) và gửi kèm mỗi request — Backend không tự sinh
   BR-11 Session ID mới → tạo batch messages mới; Session ID cũ → load lại messages array hiện có
   BR-12 Khi không có khoa phù hợp trong DB → thông báo rõ, không mapping sang khoa không liên quan

8. Ràng buộc hệ thống (Constraints)

# Ràng buộc

C-01 Phiên bản V1 là bản demo, không triển khai production thực tế
C-02 Giới hạn 100 lượt gọi AI/ngày để kiểm soát chi phí OpenAI
C-03 Hệ thống phục vụ tối đa ~50 người dùng đồng thời
C-04 Tech stack cố định: Angular 21, Python 3.19, SQLite, FastAPI
C-05 Không tích hợp với HIS (Hospital Information System) hiện có
C-06 Không hỗ trợ thanh toán online, Video call / Telemedicine
C-07 Không có ứng dụng mobile native (iOS/Android) trong V1
C-08 Không đọc / phân tích hình ảnh y tế (X-quang, MRI...)
C-09 Không tự động reschedule khi bác sĩ nghỉ đột xuất

9. Giả định và phụ thuộc (Assumptions & Dependencies)
   9.1 Giả định

# Giả định

A-01 Tất cả bác sĩ và bệnh nhân đều ở múi giờ UTC+7 (Việt Nam)
A-02 Dữ liệu ban đầu (khoa, bác sĩ, lịch làm việc) được cài đặt sẵn (seed) trước khi demo
A-03 Mỗi bác sĩ có địa chỉ email hợp lệ để nhận thông báo
A-04 OpenAI API key luôn khả dụng trong quá trình demo
A-05 Gmail SMTP được cấu hình sẵn để gửi email xác nhận
9.2 Phụ thuộc bên ngoài
Phụ thuộc Mục đích
OpenAI GPT-4o API AI engine xử lý ngôn ngữ, dự đoán bệnh, Topic Guard
LangChain Abstraction layer cho AI
langdetect Thư viện phát hiện ngôn ngữ
Gmail SMTP Gửi email xác nhận lịch hẹn

10. Phạm vi hệ thống (Scope)
    10.1 Trong phạm vi V1

# Tính năng

✅ Chatbot chỉ hỗ trợ chủ đề y tế (Topic Guard)
✅ Chatbot đa ngôn ngữ tự động nhận diện (mọi ngôn ngữ)
✅ Tiếp nhận triệu chứng qua ngôn ngữ tự nhiên
✅ Gợi ý bệnh có thể mắc phải kèm mức độ nghiêm trọng
✅ Gợi ý khoa và bác sĩ; thông báo khi chưa có chuyên khoa
✅ Kiểm tra lịch trống và đặt lịch khám tự động
✅ Gợi ý bác sĩ thay thế khi bác sĩ chọn không còn lịch trống
✅ Tự động thu thập thông tin bệnh nhân qua hội thoại
✅ Gửi email xác nhận đến bệnh nhân và bác sĩ
✅ Cổng quản trị cơ bản (Admin Portal, Doctor Portal)
10.2 Ngoài phạm vi V1

# Tính năng

❌ Thanh toán online
❌ Video call / Telemedicine
❌ Tích hợp với HIS hiện có
❌ Ứng dụng di động native (iOS/Android)
❌ Đọc & phân tích kết quả xét nghiệm / hình ảnh y tế
❌ Tự động reschedule khi bác sĩ nghỉ đột xuất

11. Mô hình dữ liệu (Data Model Summary)
    Bảng Mô tả chính
    departments Danh mục khoa khám bệnh
    disease_department_mapping Mapping bệnh → khoa
    doctors Thông tin bác sĩ (có soft delete qua is_active)
    doctor_working_hours Lịch làm việc mặc định theo tuần
    medical_examination_schedule Các slot đã BOOKED hoặc BLOCKED; slot trống tính on-demand
    patients Thông tin bệnh nhân (chỉ insert khi xác nhận đặt lịch)
    appointments Lịch hẹn khám, kèm mã MA-YYYYMMDD-XXXX
    chat_sessions Session hội thoại (UUID, tự hết hạn 24h, lưu messages JSON)
    user_accounts Tài khoản Admin/Doctor với role và bcrypt password
    Chi tiết schema SQL đầy đủ xem tại 03_Technical_Spec.md § 3.

12. Phụ lục
    12.1 Ma trận truy xuất yêu cầu (Traceability Matrix)
    UC FR chính BR liên quan Test Cases
    UC-00 FR-00-01 → FR-00-05 BR-00 TC_00_01 → TC_00_04
    UC-01 FR-01-01 → FR-01-05 — TC_01_01 → TC_01_04
    UC-02 FR-02-01 → FR-02-06 — TC_02_01 → TC_02_04
    UC-03 FR-03-01 → FR-03-06 BR-01, BR-02, BR-03, BR-04 TC_03_01 → TC_03_04
    UC-04 FR-04-01 → FR-04-03 BR-05, BR-12 TC_04_01 → TC_04_04
    UC-05 FR-05-01 → FR-05-03 BR-07, BR-08 —
    UC-06 FR-06-01 → FR-06-04 BR-02, BR-03, BR-04, BR-05 —
    UC-07 FR-07-01 → FR-07-03 BR-09 —
    UC-08 FR-08-01 → FR-08-04 BR-06, BR-08 —
    Session FR-11-01 → FR-11-06 BR-10, BR-11 —
    12.2 Luồng Conversation State Machine
    [START]
    │
    ▼
    TOPIC_GUARD ──(không y tế)──► Phản hồi từ chối → [KEEP SESSION]
    │ (y tế)
    ▼
    GREETING
    │
    ▼
    SYMPTOM_COLLECTION ─── (tối đa 3 clarify turns) ───►
    │ │
    ▼ (không rõ)
    DISEASE_PREDICTION ◄──────────────────────────── UC-04 (tổng quát)
    │
    ├─(không đủ ≥60%)──► Quay về SYMPTOM_COLLECTION
    │
    ▼
    DOCTOR_SELECTION
    │
    ├─(không có khoa)──► Thông báo → [END]
    │
    ▼
    SLOT_SELECTION
    │
    ├─(URGENT, không có slot 48h)──► Cảnh báo cấp cứu → [END]
    ├─(không có slot)──► DOCTOR_SELECTION (thay thế)
    │
    ▼
    INFO_COLLECTION
    │
    ▼
    CONFIRMATION
    │
    ▼
    COMPLETED ──► Gửi email xác nhận → [END]
    12.3 Ưu tiên tính năng (Workshop 2)
    Ưu tiên UC Tính năng
    P0 — Must Have UC-00 Topic Guard
    P0 — Must Have UC-01 Language Detection
    P0 — Must Have UC-02 Symptom Collection
    P0 — Must Have UC-03 Disease Prediction
    P0 — Must Have UC-04 Department & Doctor Suggestion
    P1 — Sprint tiếp theo UC-05 → UC-08 Auto Form Fill, Scheduling, Booking
    P2 — Sprint tiếp theo UC-09 → UC-11 Admin/Doctor Portal

Tài liệu này tổng hợp và chuẩn hóa các yêu cầu từ BRD, Functional Spec, và Technical Spec theo chuẩn IEEE 830. Mọi thay đổi yêu cầu phải được cập nhật đồ
