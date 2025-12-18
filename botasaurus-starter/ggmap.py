from src.scrape_heading_task import crawl_places, ggmap
from time import sleep
import json  # <-- 1. Import thư viện JSON
import re    # <-- (Tùy chọn) Import Regex để làm sạch tên file

# Test
# --- Hàm main để chạy (như bạn yêu cầu) ---
if __name__ == "__main__":

    try:
        while True:
            # 1. Nhận query từ người dùng
            user_input = input("\n[Google Maps] Nhập địa điểm cần tìm: ")

            # 2. Điều kiện thoát vòng lặp
            if user_input.lower() in ['exit', 'quit', 'thoat', 'q']:
                print("Đã nhận lệnh thoát. Đang đóng trình duyệt...")
                break

            # 3. Bỏ qua nếu input rỗng
            if not user_input.strip():
                continue

            # 4. Gọi hàm ggmap
            # Botasaurus sẽ tự động quản lý trình duyệt:
            # - Lần đầu tiên: Mở trình duyệt mới.
            # - Các lần sau: Sử dụng lại trình duyệt cũ (nhờ reuse_driver=True)
            ggmap(data=user_input)

    except KeyboardInterrupt:
        # Xử lý khi người dùng nhấn Ctrl+C
        print("\nĐã phát hiện (Ctrl+C). Đang đóng...")

    except Exception as e:
        print(f"Đã xảy ra lỗi nghiêm trọng: {e}")

    finally:
        # Botasaurus có cơ chế tự động dọn dẹp (shutdown)
        # khi script kết thúc.
        print("Chương trình đã kết thúc.")
