MedAssist AI — Business Requirements Document (BRD)
Tầng: High-Level · Đối tượng: Stakeholders, Product Manager, Sponsor
Version: 1.0
Date: 2026-04-18

1. BỐI CẢNH & MỤC TIÊU KINH DOANH
   Vấn đề hiện tại
   • Bệnh nhân mất nhiều thời gian gọi điện / đến trực tiếp để đặt lịch khám
   • Không biết mình nên khám khoa nào khi có triệu chứng
   • Nhân viên lễ tân phải xử lý nhiều cuộc gọi đặt lịch thủ công
   • Lịch bác sĩ không được tối ưu, dễ xảy ra trùng lịch hoặc bỏ trống
   Mục tiêu
   • Giảm thời gian đặt lịch khám từ ~10 phút xuống dưới 3 phút
   • Hỗ trợ bệnh nhân tự định hướng khoa phù hợp trước khi đến bệnh viện
   • Tự động hóa quy trình thu thập thông tin và đặt lịch
   • Tăng hiệu suất sử dụng lịch của bác sĩ

2. TỔNG QUAN SẢN PHẨM
   MedAssist AI là ứng dụng chatbot y tế thông minh, hỗ trợ bệnh nhân từ khâu khai báo triệu chứng đến đặt lịch khám tự động. Hệ thống tự nhận diện ngôn ngữ người dùng, dự đoán bệnh, gợi ý khoa/bác sĩ phù hợp và tự động điền form hẹn lịch dựa trên thông tin thu thập qua hội thoại.
   Lưu ý quan trọng: Kết quả dự đoán bệnh của hệ thống chỉ mang tính tham khảo, không thay thế chẩn đoán y tế chính thức của bác sĩ.

3. CÁC BÊN LIÊN QUAN (Stakeholders & Actors)
   Bên liên quan Vai trò Kỳ vọng chính
   Bệnh nhân Người dùng cuối Đặt lịch nhanh, dễ dùng, không cần tạo tài khoản
   Bác sĩ Người nhận lịch hẹn Nhận thông báo đúng giờ, xem được thông tin bệnh nhân trước
   Quản trị viên Vận hành hệ thống Quản lý danh mục khoa, bác sĩ, lịch làm việc
   Ban lãnh đạo bệnh viện Sponsor Báo cáo hiệu suất, giảm tải nhân sự lễ tân

4. PHẠM VI HỆ THỐNG (Scope)
   Trong phạm vi (In Scope — V1)
   • Chatbot chỉ hỗ trợ chủ đề y tế, từ chối lịch sự các chủ đề khác
   • Chatbot đa ngôn ngữ tự động nhận diện — hỗ trợ mọi ngôn ngữ
   • Tiếp nhận triệu chứng và gợi ý bệnh có thể mắc phải
   • Gợi ý khoa và bác sĩ phù hợp; thông báo khi bệnh viện chưa có chuyên khoa tương ứng
   • Kiểm tra lịch trống và đặt lịch khám tự động
   • Gợi ý bác sĩ thay thế khi bác sĩ được chọn không còn lịch trống
   • Tự động thu thập thông tin bệnh nhân qua hội thoại
   • Gửi xác nhận lịch hẹn đến bệnh nhân và bác sĩ qua email
   • Cổng quản trị cơ bản cho Admin và Bác sĩ
   Ngoài phạm vi (Out of Scope — V1)
   • Thanh toán online
   • Video call / Telemedicine
   • Tích hợp với HIS (Hospital Information System) hiện có
   • Ứng dụng di động native (iOS/Android)
   • Đọc & phân tích kết quả xét nghiệm / hình ảnh y tế
   • Tự động reschedule khi bác sĩ nghỉ đột xuất

5. CÁC CHỨC NĂNG CHÍNH (High-Level Capabilities)

# Khả năng Mô tả ngắn

C-00 Topic Guard Chỉ trả lời chủ đề y tế; từ chối lịch sự mọi chủ đề khác
C-01 Chatbot đa ngôn ngữ Tự nhận diện và phản hồi đúng ngôn ngữ — hỗ trợ mọi ngôn ngữ
C-02 Tiếp nhận triệu chứng Hiểu mô tả tự nhiên, không cần chọn từ danh sách
C-03 Gợi ý bệnh & mức độ Đưa ra các bệnh có thể mắc và phân loại khẩn cấp/thường
C-04 Định hướng khoa & bác sĩ Gợi ý khoa/bác sĩ phù hợp; thông báo rõ nếu bệnh viện chưa có chuyên khoa
C-05 Đặt lịch tự động Thu thập thông tin qua chat và tự điền form đặt lịch
C-06 Kiểm tra & tối ưu lịch Quét lịch trống theo mức độ bệnh, gợi ý thay thế khi cần
C-07 Thông báo xác nhận Gửi email xác nhận đến cả bệnh nhân và bác sĩ
C-08 Quản trị hệ thống Admin quản lý khoa, bác sĩ; Bác sĩ quản lý lịch cá nhân

6. QUY TẮC NGHIỆP VỤ QUAN TRỌNG (Key Business Rules)
   BR# Quy tắc
   BR-00 Chatbot chỉ trả lời các chủ đề liên quan đến y tế và sức khỏe — từ chối lịch sự mọi yêu cầu khác bằng ngôn ngữ của người dùng
   BR-01 Hệ thống chỉ được gợi ý, không được chẩn đoán — phải hiển thị disclaimer bắt buộc
   BR-02 Triệu chứng khẩn cấp (đau ngực, khó thở, bất tỉnh...) → ưu tiên tìm lịch trong 24–48 giờ
   BR-03 Triệu chứng trung bình → tìm lịch trong vòng 7 ngày
   BR-04 Triệu chứng nhẹ → tìm lịch tối đa 30 ngày
   BR-05 Nếu không có lịch khẩn cấp trong 48h → cảnh báo bệnh nhân đến cấp cứu ngay
   BR-06 Mỗi ca khám chuẩn là 1 tiếng
   BR-07 Bệnh nhân không cần tạo tài khoản để đặt lịch
   BR-08 Thông tin cá nhân bệnh nhân chỉ lưu vĩnh viễn sau khi xác nhận đặt lịch
   BR-09 Khi bác sĩ được yêu cầu hết lịch → hệ thống bắt buộc gợi ý bác sĩ thay thế cùng khoa
   BR-10 Session ID do Frontend tạo (UUID v4) và gửi kèm mỗi request — Backend không tự sinh session ID
   BR-11 Khi nhận session ID mới → tạo batch messages mới; session ID cũ → load lại messages array hiện có
   BR-12 Khi không có khoa phù hợp trong DB → thông báo rõ tên chuyên khoa còn thiếu, không mapping sang khoa không liên quan

7. RÀNG BUỘC & GIẢ ĐỊNH (Constraints & Assumptions)
   Ràng buộc
   • Phiên bản V1 là bản demo, không triển khai production thực tế
   • Giới hạn 100 lượt sử dụng AI/ngày để kiểm soát chi phí
   • Hệ thống phục vụ tối đa ~50 người dùng đồng thời
   Giả định
   • Tất cả bác sĩ và bệnh nhân đều ở múi giờ UTC+7 (Việt Nam)
   • Dữ liệu ban đầu (khoa, bác sĩ, lịch làm việc) được cài đặt sẵn trước khi demo
   • Bác sĩ có địa chỉ email để nhận thông báo

8. RỦI RO NGHIỆP VỤ (Business Risks)
   Rủi ro Mức độ ảnh hưởng Biện pháp
   Chatbot trả lời chủ đề ngoài y tế Trung bình Topic Guard kiểm tra mỗi tin nhắn trước khi xử lý
   AI gợi ý khoa sai khi không có chuyên khoa phù hợp Cao Fallback rõ ràng: thông báo chuyên khoa chưa có, không map sai
   AI gợi ý bệnh không chính xác gây hiểu lầm Cao Disclaimer rõ ràng, luôn nhắc đây là tham khảo
   Bác sĩ không nhận được thông báo lịch hẹn Cao Email xác nhận + bác sĩ tự kiểm tra lịch trên hệ thống
   Bệnh nhân lo ngại về bảo mật thông tin cá nhân Trung bình Không lưu PII khi chưa xác nhận; cam kết rõ về chính sách dữ liệu
   Hệ thống quá tải trong buổi demo Thấp Giới hạn rate, chuẩn bị seed data sẵn
