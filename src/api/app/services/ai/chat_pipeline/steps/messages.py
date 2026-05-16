from __future__ import annotations

from app.core.enumerations.languages_enum import Languages
from app.core.utilities.safe_dict import SafeDict

NON_MEDICAL_MSC_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "Sorry, I'm just chatbot to support healthcare. I cannot support other topic",
    "vi": "Xin lỗi, tôi chỉ là chatbot hỗ trợ y tế. Tôi không thể hỗ trợ các chủ đề khác",
    "jp": "申し訳ございません。私は医療サポート用のチャットボットです。他のトピックはサポートできません",
}, fallback_key="en")

THREAD_ALREADY_CLOSED_MSC_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "This thread was closed. Please start a new chat.",
    "vi": "Cuộc trò chuyện này đã đóng. Vui lòng bắt đầu cuộc trò chuyện mới.",
    "jp": "このスレッドは閉じられました。新しいチャットを開始してください。",
}, fallback_key="en")

THANKS_CLOSE_MSC_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "Thank you for using our service. We hope you feel better soon.",
    "vi": "Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi. Chúng tôi hy vọng bạn sớm cảm thấy tốt hơn.",
    "jp": "サービスをご利用いただきありがとうございます。早く良くなられることを願っています。",
}, fallback_key="en")

OPENAI_MISSING_MSC_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "The healthcare assistant is not configured (missing OpenAI settings).",
    "vi": "Trợ lý y tế chưa được cấu hình (thiếu cài đặt OpenAI).",
    "jp": "医療アシスタントが設定されていません（OpenAI設定が不足しています）。",
}, fallback_key="en")

BASE_ASSISTANT_INSTRUCTION_DICT: SafeDict[Languages, str] = SafeDict({
    "en": (
        "You are a healthcare triage and booking assistant. Reply briefly in the user's language.\n"
        "During triage, focus on picking the right department or asking exactly one short clarifying question.\n"
        "Do not give long medical advice before routing. Do not tell the user to contact an external clinic "
        "or hospital when this app supports internal booking."
    ),
    "vi": (
        "Bạn là trợ lý phân luồng khám và đặt lịch. Trả lời ngắn bằng ngôn ngữ người dùng.\n"
        "Trong giai đoạn phân loại khoa, chỉ tập trung chọn đúng khoa hoặc hỏi một câu làm rõ ngắn.\n"
        "Không tư vấn dài trước khi phân khoa. Không bảo người dùng liên hệ cơ sở y tế/phòng khám bên ngoài "
        "khi ứng dụng đã có luồng đặt lịch nội bộ."
    ),
    "jp": (
        "あなたは診療科振り分けと予約支援のアシスタントです。ユーザーの言語で簡潔に答えてください。\n"
        "トリアージ中は適切な診療科を決めるか、短い確認質問を1つだけにしてください。\n"
        "振り分け前に長い医学アドバイスをしないでください。このアプリが院内予約に対応しているときは、 "
        "外部の医療機関へ連絡するよう促さないでください。"
    ),
}, fallback_key="en")

BOOKING_PROMPT_DIRECT_REPLY_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "The most suitable department is {0}. Would you like to pre-book a visit there? (yes/no)",
    "vi": (
        "Khoa phù hợp nhất là {0}. Bạn có muốn đặt lịch khám trước tại khoa này không? (có/không)"
    ),
    "jp": (
        "最も適した診療科は {0} です。この診療科で事前に予約しますか？（はい/いいえ）"
    ),
}, fallback_key="en")

APPOINTMENT_FORM_READY_DIRECT_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "We have enough details to continue. Please tap the button to open the registration form.",
    "vi": (
        "Mình đã có đủ thông tin cần thiết. Vui lòng bấm nút để mở biểu mẫu đăng ký đặt lịch."
    ),
    "jp": "必要な情報が揃いました。登録フォームを開くボタンをタップしてください。",
}, fallback_key="en")

DIRECT_REPLY_PII_COLLECTION_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "Please share your full name, date of birth, gender, and phone.",
    "vi": "Vui lòng chia sẻ họ tên đầy đủ, ngày sinh, giới tính và số điện thoại của bạn.",
    "jp": "氏名、生年月日、性別、電話番号を教えてください。",
}, fallback_key="en")

TRIAGE_CAP_REACHED_INSTRUCTION_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "INTERNAL: Triage cap reached. Department is General Internal Medicine. Acknowledge briefly, then ask if they want to pre-book a visit.",
    "vi": "INTERNAL: Đã đạt giới hạn phân loại triệu chứng. Phòng khám là Nội tổng hợp. Xác nhận ngắn gọn, sau đó hỏi họ có muốn đặt lịch khám trước không.",
    "jp": "INTERNAL: トリアージの上限に達しました。診療科は一般内科です。簡潔に確認し、事前予約を希望するか尋ねてください。",
}, fallback_key="en")

TRIAGE_SHORT_QUESTION_FALLBACK_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "Could you describe your main symptom?",
    "vi": "Bạn có thể mô tả triệu chứng chính của mình không?",
    "jp": "主な症状を教えていただけますか？",
}, fallback_key="en")

TRIAGE_CLARIFICATION_INSTRUCTION_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "INTERNAL: You need a bit more information. Ask only this short question: {0}",
    "vi": "INTERNAL: Bạn cần thêm một chút thông tin. Chỉ hỏi câu ngắn này: {0}",
    "jp": "INTERNAL: もう少し情報が必要です。この短い質問だけを尋ねてください: {0}",
}, fallback_key="en")

BOOKING_ACCEPTED_PII_INSTRUCTION_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "INTERNAL: The user agreed to pre-book. Continue collecting PII.",
    "vi": "INTERNAL: Người dùng đã đồng ý đặt lịch trước. Tiếp tục thu thập thông tin cá nhân.",
    "jp": "INTERNAL: ユーザーは事前予約に同意しました。個人情報の収集を続けてください。",
}, fallback_key="en")

REGISTRATION_READY_INSTRUCTION_DICT: SafeDict[Languages, str] = SafeDict({
    "en": "INTERNAL: The registration form is ready; the app should show a button to open the booking form.",
    "vi": "INTERNAL: Biểu mẫu đăng ký đã sẵn sàng; ứng dụng nên hiển thị nút để mở biểu mẫu đặt lịch.",
    "jp": "INTERNAL: 登録フォームの準備ができました。アプリは予約フォームを開くボタンを表示してください。",
}, fallback_key="en")
