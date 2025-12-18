from src.scrape_heading_task import start_crawl_ggmap
from src.crawl_chrome import get_description
from time import sleep
import json
import re
import os
from datetime import datetime


def test_0001():
    inputs = [
        {
            "type": "Nhà hàng",
            "street": "",
            "ward": "Bạch Mai",
            "county": "Hai Bà Trưng",
            "city": "Hà Nội",
            "province": "",
            "numResult": 100
        }
    ]

    # Đảm bảo thư mục đích tồn tại
    output_dir = os.path.join("output", "data")
    os.makedirs(output_dir, exist_ok=True)

    for item in inputs:
        print(f"Đang xử lý: {item}")
        query = f"{item['type']} {item['street']} {item['ward']} {item['county']} {item['city']} {item['province']} Việt Nam"
        # print(f"Đang xử lý: {query}")

        # --- Gọi hàm crawl ---
        data = start_crawl_ggmap(item)

        # --- Tạo tên file an toàn từ query ---
        safe_name = re.sub(r'[^\w\s-]', '', query.lower())  # bỏ ký tự đặc biệt
        # thay khoảng trắng bằng "_"
        safe_name = re.sub(r'[\s]+', '_', safe_name).strip('-_')
        if len(safe_name) > 100:
            safe_name = safe_name[:100]

        # --- Thêm mốc thời gian ---
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # --- Tạo tên file đầy đủ ---
        file_name = f"{timestamp}_{safe_name}.json"
        file_path = os.path.join(output_dir, file_name)

        # --- Lưu dữ liệu ra file ---
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"✅ Đã lưu dữ liệu thành công vào file: {file_path}")
        except Exception as e:
            print(f"❌ Lỗi khi đang lưu file {file_path}: {e}")

        print("="*50)
        sleep(1)  # nghỉ 1 giây để tránh bị giới hạn request


def test_0002():
    queries = [
        "Cầu rồng đà nẵng việt nam",
        # "Bạn có thể thêm các query khác ở đây"
    ]

    # Dùng enumerate để lấy chỉ số (i) cho mỗi query, tiện cho việc đặt tên file
    for i, query in enumerate(queries):
        print(f"Đang xử lý: {query}")
        description = get_description(query)

        # --- THAY THẾ PRINT(DATA) BẰNG LƯU FILE JSON ---

        # 2. Tạo một tên file an toàn từ query
        # Chuyển query thành chữ thường, xóa ký tự đặc biệt, thay khoảng trắng bằng "_"
        safe_name = re.sub(r'[^\w\s-]', '', query.lower())
        safe_name = re.sub(r'[\s]+', '_', safe_name).strip('-_')

        # Đặt tên file (ví dụ: results_0_quan_nhau_duong_le_dai_hanh_da_nang_viet_nam.json)
        # Cắt ngắn nếu tên quá dài
        if len(safe_name) > 100:
            safe_name = safe_name[:100]

        print(description)  # <-- Dòng này đã được thay thế
        print("="*50)
        sleep(1)  # nghỉ 1 giây (như trong code gốc)


# Test
if __name__ == "__main__":
    test_0001()
    # test_0002()
