
import re
import time
from src.places.clean_text import clean_text
from src.places.working_hours.format_working_hours import format_working_hours


def get_working_hours(driver):
    hours = []
    try:
        # 1. Tìm và Click nút mở rộng giờ (nếu nó đang đóng - aria-expanded="false")
        # Selector này nhắm vào nút dropdown có chứa icon clock
        expand_btn_selector = 'div[role="button"][jsaction*="pane.openhours"]'

        # Kiểm tra xem có nút này không và trạng thái aria-expanded
        btn = driver.select(expand_btn_selector)
        if btn and btn.get_attribute("aria-expanded") == "false":
            btn.click()
            # Cần sleep nhẹ để chờ bảng render ra
            time.sleep(1)

        # 2. Lấy tất cả các dòng trong bảng giờ
        # Class "y0skZc" là class định danh cho mỗi dòng (row) trong bảng giờ
        rows = driver.select_all('table tr.y0skZc')

        for row in rows:
            # Lấy Thứ (Day) - Class "ylH6lf"
            day_el = row.select('.ylH6lf')

            # Lấy Giờ (Time) - Class "mxowUb"
            time_el = row.select('.mxowUb')

            if day_el and time_el:
                # Dùng text_content() hoặc text tùy thư viện bạn dùng
                # clean_text là hàm bạn đã có để xóa khoảng trắng thừa
                d = clean_text(day_el.text)
                t = clean_text(time_el.text)

                # Format lại thành chuỗi: "Monday: 8:30 AM – 8:30 PM"
                hours.append(f"{d}: {t}")

    except Exception as e:
        print(f"Error getting hours: {e}")
        pass

# Kết quả hours lúc này sẽ là một List các string, ví dụ:
# ['Friday: 8:30 AM–8:30 PM', 'Saturday: 8:30 AM–8:30 PM', ...]
# List này sẽ được truyền thẳng vào hàm format_working_hours mình đã viết ở bước trước.
    working_hours = format_working_hours(hours)
    return working_hours
