import re
import unicodedata


def remove_vietnamese_accents(text):
    """
    Chuyển đổi chuỗi tiếng Việt có dấu thành không dấu.
    Ví dụ: "Hồ Chí Minh" -> "Ho Chi Minh"
    """
    if not text:
        return ""

    # 1. Xử lý thủ công chữ đ/Đ (vì NFD không tách được chữ này)
    text = re.sub(r'[đ]', 'd', text)
    text = re.sub(r'[Đ]', 'D', text)

    # 2. Chuẩn hóa Unicode sang dạng NFD (Canonical Decomposition)
    # Bước này tách ký tự gốc và dấu câu ra (Ví dụ: ồ -> o + ` + ^)
    normalized = unicodedata.normalize('NFD', text)

    # 3. Lọc bỏ các ký tự thuộc loại 'Mn' (Mark, Nonspacing - chính là các dấu)
    result = ''.join(
        char for char in normalized if unicodedata.category(char) != 'Mn')

    return result


# === TEST ===
# input_str = "Hồ Chí Minh - TP. Đà Nẵng"
# output_str = remove_vietnamese_accents(input_str)

# print(f"Gốc: {input_str}")
# print(f"Sau khi chuyển: {output_str}")
