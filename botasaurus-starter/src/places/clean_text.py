import re
import unicodedata


def clean_text(text):
    if not text:
        return ""
    # Chuẩn hóa unicode (giữ dấu tiếng Việt)
    text = unicodedata.normalize("NFC", text)
    # Loại bỏ ký tự đặc biệt không cần thiết
    text = re.sub(r"[^\w\s.,:/@-]", "", text)
    text = text.replace("Đa Nang", "Đà Nẵng").replace(
        "Đang", "Đằng"
    )  # Sửa lỗi thông thường
    return re.sub(r"\s+", " ", text).strip()
