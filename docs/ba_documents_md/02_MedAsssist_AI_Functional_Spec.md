MedAssist AI — Functional Specification
Tầng: Mid-Level · Đối tượng: BA, Product Owner, QA
Version: 1.0  
Date: 2026-04-18  
Tham chiếu: 01_BRD.docx

1. USE CASES CHI TIẾT
   Workshop 2 Scope: UC-00, UC-01, UC-02, UC-03, UC-04
   UC-05 đến UC-11 thuộc các sprint tiếp theo.

UC-00: Kiểm soát chủ đề hội thoại (Topic Guard)
• Actor: Bệnh nhân, AI Engine
• Trigger: Bệnh nhân gửi bất kỳ tin nhắn nào
• Precondition: Session đang hoạt động
Main Flow:

1. Trước mọi xử lý khác, AI Engine phân tích nội dung tin nhắn
2. Nếu liên quan y tế (triệu chứng, bệnh, đặt lịch, hỏi về bác sĩ/khoa...) → tiếp tục sang UC-01
3. Nếu không liên quan y tế → phản hồi lịch sự bằng đúng ngôn ngữ của người dùng:
   "Xin lỗi, tôi chỉ có thể hỗ trợ các vấn đề liên quan đến sức khỏe và y tế. Bạn có muốn mô tả triệu chứng hoặc đặt lịch khám không?"
4. Session vẫn được giữ nguyên — người dùng có thể tiếp tục hội thoại y tế sau đó
   Danh sách chủ đề bị từ chối (ví dụ):
   • Thời tiết, nấu ăn, du lịch
   • Lập trình, công nghệ
   • Tư vấn pháp lý, tài chính
   • Giải trí, thể thao, chính trị
   Postcondition: Session giữ nguyên; chỉ phản hồi từ chối, không xử lý gì thêm

UC-01: Phát hiện ngôn ngữ & Phản hồi đa ngôn ngữ
• Actor: Bệnh nhân, AI Engine
• Trigger: Bệnh nhân gửi tin nhắn đầu tiên
• Precondition: Bệnh nhân mở giao diện chatbot
Main Flow: 5. Bệnh nhân gõ tin nhắn bất kỳ 6. AI phân tích ngôn ngữ — hỗ trợ mọi ngôn ngữ, không giới hạn 7. Hệ thống lưu ngôn ngữ vào session hiện tại 8. Chatbot phản hồi bằng đúng ngôn ngữ đó
Alternative Flow:
• Nếu bệnh nhân chuyển ngôn ngữ giữa chừng → hệ thống tự cập nhật ngôn ngữ session và phản hồi theo ngôn ngữ mới
Constraint: Ngôn ngữ detect dựa trên nội dung tin nhắn thực tế, không cần người dùng khai báo
Postcondition: Session có thuộc tính ngôn ngữ được gán chính xác

UC-02: Khai báo triệu chứng
• Actor: Bệnh nhân, AI Engine
• Trigger: Bệnh nhân nhập mô tả triệu chứng vào chat
• Precondition: UC-01 đã hoàn thành
Main Flow: 9. Chatbot hỏi dẫn dắt: "Bạn đang gặp phải triệu chứng gì?" 10. Bệnh nhân mô tả tự do bằng ngôn ngữ tự nhiên 11. AI trích xuất các thông tin: bộ phận cơ thể, tính chất triệu chứng, thời gian xuất hiện, mức độ đau 12. Nếu thông tin chưa đủ → chatbot hỏi thêm câu làm rõ (tối đa 3 lượt hỏi thêm) 13. Triệu chứng được tổng hợp thành danh sách có cấu trúc
Validation:
• Nếu bệnh nhân nhập nội dung không liên quan đến triệu chứng → chatbot nhắc nhở và hỏi lại
• Nếu sau 3 lượt vẫn không thu thập được triệu chứng rõ ràng → chuyển sang UC-04 với gợi ý khoa tổng quát
Postcondition: Có danh sách triệu chứng có cấu trúc để đưa vào UC-03

UC-03: Dự đoán bệnh (Disease Prediction)
• Actor: AI Engine
• Trigger: Sau khi UC-02 thu thập đủ triệu chứng
• Precondition: Có ít nhất 1 triệu chứng có cấu trúc từ UC-02
Main Flow: 14. AI Engine xử lý danh sách triệu chứng 15. Trả về top 3–5 bệnh có khả năng mắc phải kèm mức độ tin cậy (%) 16. Chỉ hiển thị bệnh có độ tin cậy ≥ 60% 17. Gắn nhãn mức độ nghiêm trọng tổng thể: URGENT / MODERATE / MILD 18. Hiển thị kết quả cho bệnh nhân dưới dạng dễ hiểu kèm disclaimer bắt buộc
Business Rule Override:
• Nếu triệu chứng chứa từ khóa nguy hiểm (đau ngực, khó thở, bất tỉnh, liệt, co giật...) → bắt buộc gắn `URGENT` bất kể kết quả AI
Alternative Flow:
• Nếu không có bệnh nào đạt ≥ 60% → hiển thị thông báo "Không đủ thông tin để dự đoán, vui lòng mô tả thêm" và quay về UC-02
Postcondition: Session có severity level được gán; sẵn sàng cho UC-04

UC-04: Gợi ý Khoa & Bác sĩ
• Actor: Bệnh nhân, AI Engine
• Trigger: Sau khi UC-03 có kết quả dự đoán bệnh
• Precondition: Có danh sách bệnh dự đoán từ UC-03
Main Flow: 19. Hệ thống tra cứu mapping: bệnh dự đoán → khoa phù hợp (từ database) 20. [Happy Path] Nếu tìm được khoa phù hợp:
• Hiển thị danh sách khoa gợi ý kèm mô tả ngắn
• Hiển thị danh sách bác sĩ của từng khoa (ảnh, tên, chức danh, chuyên môn)
• Bệnh nhân chọn khoa và/hoặc bác sĩ cụ thể
• Nếu bệnh nhân không chọn → AI tự gợi ý bác sĩ phù hợp nhất và xác nhận với bệnh nhân 21. [Alternative Path — Không có khoa phù hợp] Nếu không tìm được khoa nào trong DB:
• Chatbot thông báo bằng ngôn ngữ của người dùng:
"Rất tiếc, bệnh viện hiện chưa có chuyên khoa phù hợp để điều trị [tên bệnh/nhóm bệnh]. Bạn có thể liên hệ trực tiếp với bệnh viện để được tư vấn thêm."
• Hệ thống không cố gắng mapping sang khoa không liên quan
• Kết thúc flow tại đây, không tiếp tục đặt lịch
Postcondition (Happy Path): Có doctor_id và department_id được chọn; chuyển sang UC-06
Postcondition (No Department): Flow kết thúc; bệnh nhân nhận thông tin liên hệ bệnh viện

UC-05: Thu thập thông tin bệnh nhân (Auto Form Fill)
• Actor: Bệnh nhân, AI Engine
• Trigger: Bệnh nhân đồng ý đặt lịch khám
• Precondition: UC-04 đã xác định được bác sĩ và khoa
Main Flow: 22. Chatbot thu thập thông tin qua hội thoại tự nhiên, từng bước:
• Họ và tên đầy đủ
• Ngày sinh (dd/mm/yyyy)
• Giới tính
• Số điện thoại
• Email
• Số CCCD hoặc mã BHYT (tuỳ chọn)
• Địa chỉ 23. AI validate từng trường ngay khi nhận (định dạng SĐT, email, ngày tháng) 24. Nếu sai định dạng → chatbot thông báo và yêu cầu nhập lại 25. Sau khi đủ thông tin → tự động điền vào form hẹn lịch 26. Hiển thị form tóm tắt để bệnh nhân xác nhận trước khi submit
Validation Rules:
Trường Quy tắc
Họ tên Bắt buộc, tối thiểu 2 từ
Ngày sinh Định dạng dd/mm/yyyy, không được là ngày tương lai
Số điện thoại Bắt buộc, 10 chữ số, bắt đầu bằng 0
Email Định dạng hợp lệ, không bắt buộc
CCCD 12 chữ số nếu nhập, không bắt buộc
Postcondition: Form hẹn lịch được điền đầy đủ; sẵn sàng cho UC-08

UC-06: Kiểm tra lịch trống của bác sĩ
• Actor: Bệnh nhân, AI Engine
• Trigger: Sau khi chọn xong bác sĩ từ UC-04
• Precondition: Có doctor_id và severity level
Main Flow: 27. Xác định khoảng thời gian tìm kiếm dựa theo severity:
• URGENT → trong vòng 24–48 giờ tới
• MODERATE → trong vòng 7 ngày tới
• MILD → trong vòng tối đa 30 ngày tới 28. Truy vấn lịch để tìm các slot còn trống của bác sĩ trong khoảng thời gian đó 29. Hiển thị tối đa 10 slot gần nhất để bệnh nhân chọn 30. Bệnh nhân chọn một slot
Alternative Flow:
• Nếu không có slot nào trong khoảng thời gian → chuyển sang UC-07
Special Case:
• Nếu severity là URGENT và không có slot trong 48h → hiển thị cảnh báo đỏ: "Tình trạng của bạn cần được khám gấp. Vui lòng đến phòng cấp cứu ngay lập tức."
Postcondition: Có slot thời gian được chọn; chuyển sang UC-05 hoặc UC-08

UC-07: Gợi ý bác sĩ thay thế
• Actor: AI Engine, Bệnh nhân
• Trigger: Không tìm được slot trống cho bác sĩ được yêu cầu trong UC-06
• Precondition: Đã xác định department_id; bác sĩ yêu cầu không còn slot phù hợp
Main Flow: 31. Hệ thống thông báo: "Bác sĩ [Tên] hiện không có lịch trống trong thời gian phù hợp với tình trạng của bạn" 32. Tìm các bác sĩ khác cùng khoa có slot trống trong cùng khoảng thời gian 33. Hiển thị danh sách bác sĩ thay thế kèm slot sớm nhất của mỗi bác sĩ 34. Bệnh nhân chọn một bác sĩ thay thế → quay lại UC-06 với bác sĩ mới 35. Hoặc bệnh nhân chọn "Chờ bác sĩ ban đầu" → hệ thống mở rộng khoảng tìm kiếm thêm 30 ngày và hiển thị slot gần nhất
Postcondition: Có bác sĩ và slot mới được xác nhận; tiếp tục UC-05 → UC-08

UC-08: Đặt lịch khám (Book Appointment)
• Actor: Bệnh nhân
• Trigger: Bệnh nhân xác nhận thông tin và nhấn Submit
• Precondition: UC-05 và UC-06 hoàn thành; bệnh nhân đã xem và xác nhận form
Main Flow: 36. Hệ thống kiểm tra slot vẫn còn trống (tránh race condition) 37. Tạo bản ghi bệnh nhân trong database (nếu chưa tồn tại) 38. Tạo bản ghi lịch hẹn (appointment) với trạng thái PENDING 39. Khóa slot 1 giờ trong lịch của bác sĩ, chuyển trạng thái thành BOOKED 40. Gửi email xác nhận đến bệnh nhân (kèm mã đặt lịch, thời gian, tên bác sĩ, phòng khám) 41. Gửi email thông báo đến bác sĩ (kèm thông tin bệnh nhân, triệu chứng tóm tắt, thời gian) 42. Chatbot hiển thị xác nhận thành công với mã đặt lịch
Alternative Flow:
• Nếu slot vừa bị người khác đặt → thông báo "Khung giờ này vừa được đặt, vui lòng chọn lại" và quay về UC-06
Postcondition: Lịch hẹn được tạo; cả bệnh nhân và bác sĩ đều nhận được xác nhận

UC-09: Quản lý Khoa (Admin)
• Actor: Admin
• Trigger: Admin đăng nhập vào portal quản trị
Chức năng:
• Xem danh sách tất cả các khoa
• Thêm khoa mới (tên, mô tả, chuyên môn)
• Chỉnh sửa thông tin khoa
• Xóa khoa (chỉ được xóa nếu không có bác sĩ đang thuộc khoa đó)
• Quản lý danh sách bệnh được mapping vào từng khoa

UC-10: Quản lý Bác sĩ (Admin)
• Actor: Admin
• Trigger: Admin truy cập mục quản lý bác sĩ
Chức năng:
• Xem danh sách bác sĩ (có thể lọc theo khoa)
• Thêm bác sĩ mới (thông tin cá nhân, khoa, chức danh, chuyên môn, ảnh, email)
• Chỉnh sửa thông tin bác sĩ
• Thiết lập lịch làm việc mặc định hàng tuần (thứ mấy, từ giờ nào đến giờ nào)
• Vô hiệu hóa tài khoản bác sĩ (không xóa để giữ lịch sử)

UC-11: Quản lý Lịch Khám (Admin & Bác sĩ)
• Actor: Admin, Bác sĩ
• Trigger: Admin hoặc Bác sĩ đăng nhập vào portal
Chức năng — Admin:
• Xem lịch tổng quan của tất cả bác sĩ theo ngày/tuần/tháng
• Block lịch cho bác sĩ bất kỳ (đánh dấu ngày nghỉ, họp, v.v.)
• Xem danh sách lịch hẹn đã đặt
Chức năng — Bác sĩ:
• Xem lịch của bản thân theo ngày/tuần
• Tự block lịch nghỉ của mình
• Xem thông tin chi tiết từng bệnh nhân trong lịch hẹn
• Hủy lịch hẹn của bản thân (hệ thống tự gửi email thông báo cho bệnh nhân)

2. FEATURES BREAKDOWN THEO PRIORITY
   Module 1: AI Chatbot Engine
   Feature ID Feature Priority Workshop 2 Scope Ghi chú
   F-00 Topic Guard (chỉ trả lời chủ đề y tế) Must Have ✅ Tuần này Kiểm tra trước mọi xử lý
   F-01 Nhận diện ngôn ngữ tự động — mọi ngôn ngữ Must Have ✅ Tuần này
   F-02 Trích xuất triệu chứng từ text tự nhiên Must Have ✅ Tuần này
   F-03 Dự đoán bệnh + mức độ tin cậy Must Have ✅ Tuần này Chỉ hiện kết quả ≥ 60%
   F-04 Phân loại mức độ nghiêm trọng Must Have ✅ Tuần này Có keyword override list
   F-04b Department Fallback — báo lỗi khi không có khoa phù hợp Must Have ✅ Tuần này
   F-05 Thu thập thông tin qua hội thoại Must Have ⏳ Sprint sau
   F-06 Hỏi thêm câu làm rõ khi chưa đủ thông tin Should Have ⏳ Sprint sau Tối đa 3 lượt
   F-07 Session-based Message Batching (OpenAI messages array) Must Have ✅ Tuần này Giữ thống nhất trong session
   F-07b Session ID do FE tạo, BE nhận và map vào batch Must Have ✅ Tuần này
   Module 2: Đặt lịch khám
   Feature ID Feature Priority Ghi chú
   F-08 Tìm lịch theo khoảng thời gian động (severity) Must Have
   F-09 Kiểm tra lịch trống của bác sĩ Must Have
   F-10 Gợi ý bác sĩ thay thế Must Have
   F-11 Khóa slot 1 giờ khi đặt lịch Must Have
   F-12 Gửi xác nhận qua email (bệnh nhân + bác sĩ) Must Have
   F-13 Hủy / đổi lịch hẹn Should Have V1: chỉ hủy thủ công
   Module 3: Quản lý Khoa & Bác sĩ
   Feature ID Feature Priority Ghi chú
   F-14 CRUD Khoa Must Have
   F-15 CRUD Bác sĩ + Profile Must Have
   F-16 Quản lý mapping bệnh → khoa Must Have Seed sẵn ~50 bệnh phổ biến
   F-17 Thiết lập lịch làm việc tuần của bác sĩ Must Have
   F-18 Hiển thị profile công khai của bác sĩ Should Have Ảnh, chuyên môn, kinh nghiệm
   Module 4: Giao diện người dùng
   Feature ID Feature Priority Ghi chú
   F-19 Giao diện chat (bong bóng tin nhắn, typing indicator) Must Have
   F-20 Form hẹn lịch tự điền (có thể chỉnh sửa) Must Have
   F-21 Danh sách bác sĩ & khoa Must Have
   F-22 Giao diện chọn ngày/giờ (lịch + slot) Must Have
   F-23 Cổng quản trị (Admin + Bác sĩ) Must Have Minimal cho demo
   F-24 Giao diện tương thích điện thoại (Mobile-first) Must Have Ưu tiên cao
   F-25 Phản hồi streaming (chữ hiện dần từng từ) Must Have Giống ChatGPT
   Module 5: Backend & Tích hợp
   Feature ID Feature Priority Ghi chú
   F-26 API nhận/gửi tin nhắn chatbot Must Have
   F-27 API phân tích triệu chứng Must Have
   F-28 API truy vấn lịch (có lọc theo khoảng thời gian) Must Have
   F-29 API CRUD lịch hẹn Must Have
   F-30 API quản lý Khoa & Bác sĩ Must Have
   F-31 Dịch vụ gửi email thông báo Should Have
   F-32 Xác thực & phân quyền (Admin/Bác sĩ) Must Have

3. CONVERSATION FLOW TỔNG THỂ
   [BẮT ĐẦU]
   │
   ▼
   [Phát hiện ngôn ngữ] ◄──── UC-01
   │
   ▼
   [Chào hỏi & Hỏi triệu chứng] ◄──── UC-02
   │
   ▼
   [Trích xuất triệu chứng bằng AI]
   │── Cần thêm thông tin? ──► [Hỏi thêm (tối đa 3 lần)] ──┐
   │ │
   ◄──────────────────────────────────────────────────────────┘
   │
   ▼
   [Dự đoán bệnh + Phân loại mức độ] ◄──── UC-03
   │── URGENT + từ khóa nguy hiểm? ──► [Cảnh báo cấp cứu]
   │
   ▼
   [Mapping sang Khoa → Hiển thị danh sách Bác sĩ] ◄──── UC-04
   │
   ▼
   [Bệnh nhân có chọn Bác sĩ?]
   │── Có ──► [Kiểm tra lịch trống trong time window] ◄──── UC-06
   │ │── Có lịch trống ──► [Hiển thị slots]
   │ │── Không có lịch ──► [Gợi ý Bác sĩ thay thế] ◄──── UC-07
   │── Không ──► [AI gợi ý Bác sĩ tốt nhất] ──► [Kiểm tra lịch]
   │
   ▼
   [Bệnh nhân chọn Slot thời gian]
   │
   ▼
   [Thu thập thông tin cá nhân qua chat] ◄──── UC-05
   │
   ▼
   [Tự điền Form hẹn lịch]
   │
   ▼
   [Bệnh nhân xem & Xác nhận]
   │
   ▼
   [Tạo lịch hẹn + Khóa slot] ◄──── UC-08
   │
   ▼
   [Gửi email xác nhận (Bệnh nhân + Bác sĩ)]
   │
   ▼
   [KẾT THÚC]

4. QUY TẮC PHÂN LOẠI MỨC ĐỘ NGHIÊM TRỌNG
   Mức độ Điều kiện kích hoạt Khoảng tìm lịch Hành động đặc biệt
   URGENT Từ khóa nguy hiểm hoặc AI classify 24 – 48 giờ Nếu không có slot: cảnh báo đến cấp cứu
   MODERATE AI classify triệu chứng trung bình 7 ngày Không
   MILD AI classify triệu chứng nhẹ Tối đa 30 ngày Không
   Danh sách từ khóa nguy hiểm (override list — tối thiểu):
   đau ngực, khó thở, thở dốc, bất tỉnh, mất ý thức, liệt, co giật, đột quỵ, nôn ra máu, tiểu ra máu nhiều, sốt co giật, chấn thương đầu

5. PHÂN QUYỀN NGƯỜI DÙNG
   Chức năng Admin Bác sĩ Bệnh nhân
   CRUD Khoa ✅ ❌ ❌
   CRUD Bác sĩ ✅ ❌ ❌
   Xem lịch tất cả bác sĩ ✅ ❌ ❌
   Xem lịch bản thân ✅ ✅ ❌
   Block lịch nghỉ ✅ ✅ (bản thân) ❌
   Hủy lịch hẹn ✅ ✅ (bản thân) ❌
   Dùng chatbot & đặt lịch ❌ ❌ ✅
   Tra cứu lịch đã đặt ❌ ❌ ✅ (SĐT + mã)

6. SESSION & BATCHING MECHANISM
   Nguyên tắc
   Quy tắc Chi tiết
   Ai tạo session_id Frontend (UUID v4)
   Khi nhận session_id mới BE tạo batch mới, khởi tạo messages array rỗng
   Khi nhận session_id cũ BE load messages array từ DB, append tin nhắn mới
   Không lưu lịch sử vĩnh viễn Messages chỉ tồn tại trong session (TTL 24h)
   Giữ thống nhất trong session Toàn bộ messages array được gửi kèm mọi lần gọi OpenAI
   Cấu trúc messages (OpenAI format)
   [
   {"role": "system", "content": "Chỉ trả lời y tế. Ngôn ngữ tự động theo user..."},
   {"role": "user", "content": "Tôi bị đau đầu và sốt"},
   {"role": "assistant", "content": "Bạn đau đầu từ bao lâu rồi?"},
   {"role": "user", "content": "Từ hôm qua, khoảng 38.5 độ"}
   ]
   Request format từ FE
   {
   "session_id": "uuid-v4-generated-by-fe",
   "message": "Nội dung tin nhắn của user"
   }

7. EMAIL TEMPLATES
   Email xác nhận gửi Bệnh nhân
   Tiêu đề: [MedAssist AI] Xác nhận lịch hẹn khám bệnh #{{appointment_code}}

Nội dung:

- Mã lịch hẹn: {{appointment_code}}
- Bác sĩ: {{doctor_name}} — {{doctor_title}}
- Khoa: {{department_name}}
- Thời gian: {{scheduled_at}} (1 giờ)
- Địa điểm / Phòng khám: {{location}}
- Triệu chứng đã khai báo: {{symptoms_summary}}

Lưu ý: Vui lòng đến trước 15 phút và mang theo CCCD/thẻ BHYT.
Ngôn ngữ: theo ngôn ngữ session của bệnh nhân
Email thông báo gửi Bác sĩ
Tiêu đề: [MedAssist AI] Lịch hẹn mới — {{scheduled_at}}

Nội dung:

- Bệnh nhân: {{patient_name}}
- Số điện thoại: {{patient_phone}}
- Thời gian: {{scheduled_at}}
- Mã lịch hẹn: {{appointment_code}}
- Triệu chứng: {{symptoms_summary}}
- Bệnh dự đoán: {{predicted_diseases}}
- Mức độ: {{severity}}
  Ngôn ngữ: luôn là Tiếng Việt
