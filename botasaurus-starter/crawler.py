import os
import json
import re
from datetime import datetime
from time import sleep
from src.scrape_heading_task import start_crawl_ggmap


def run_crawler_logic(inputs):
    """
    Hàm này nhận inputs từ giao diện và thực hiện crawl
    """
    output_dir = os.path.join("output", "data")
    os.makedirs(output_dir, exist_ok=True)

    logs = []  # Để trả về giao diện hiển thị
    results_paths = []

    for item in inputs:
        msg_start = f"🚀 Đang xử lý: {item['type']} - {item['ward']}, {item['county']}, {item['city']}"
        print(msg_start)
        logs.append(msg_start)

        # Tạo query
        query = f"{item['type']} {item['street']} {item['ward']} {item['county']} {item['city']} {item['province']} Việt Nam"

        # --- Gọi hàm crawl ---
        try:
            data = start_crawl_ggmap(item)  # Gọi hàm thực tế của bạn

            # --- Lưu file ---
            safe_name = re.sub(r'[^\w\s-]', '', query.lower())
            safe_name = re.sub(r'[\s]+', '_', safe_name).strip('-_')
            if len(safe_name) > 100:
                safe_name = safe_name[:100]

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"{timestamp}_{safe_name}.json"
            file_path = os.path.join(output_dir, file_name)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            msg_success = f"✅ Đã lưu: {file_name}"
            logs.append(msg_success)
            results_paths.append(file_path)

        except Exception as e:
            msg_err = f"❌ Lỗi: {e}"
            logs.append(msg_err)

    return logs, results_paths
