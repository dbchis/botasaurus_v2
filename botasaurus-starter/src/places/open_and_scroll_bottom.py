import time
from botasaurus.browser import Driver


def open_and_scroll_to_bottom(driver: Driver):
    """
    Hàm click vào tab Review và cuộn xuống tận cùng.
    """
    # 1. Selector người dùng cung cấp
    # Lưu ý: Nếu trình duyệt tiếng Việt, aria-label sẽ là "Bài đánh giá"
    # Code này ưu tiên tìm "Reviews", nếu không thấy sẽ thử "Bài đánh giá" để tránh lỗi.
    reviews_tab_selector = 'button[aria-label*="Reviews"][role="tab"]'

    if not driver.select(reviews_tab_selector):
        # Fallback cho tiếng Việt
        reviews_tab_selector = 'button[aria-label*="Bài đánh giá"][role="tab"]'

    # 2. Click mở tab
    if driver.select(reviews_tab_selector):
        print(">>> Đang click tab Reviews...")
        driver.click(reviews_tab_selector)
        time.sleep(2)  # Chờ panel review tải ra
    else:
        print(">>> Không tìm thấy tab Reviews (hoặc sai ngôn ngữ).")
        return

    # 3. Xác định khung cuộn (Scroll Container)
    # Google Maps thường đặt thanh cuộn trong div có class 'm6QErb'
    # Ta cần chọn đúng div chứa review.
    scroll_div = driver.select('div.m6QErb:nth-of-type(2)')

    # Fallback nếu selector trên không trúng (đôi khi nó là div[role="main"])
    if not scroll_div:
        scroll_div = driver.select('div.m6QErb')

    if not scroll_div:
        print(">>> Không tìm thấy khung để cuộn.")
        return

    print(">>> Bắt đầu cuộn xuống đáy...")

    # 4. Logic cuộn vô tận (Infinite Scroll Loop)
    last_height = driver.execute_script(
        "return arguments[0].scrollHeight", scroll_div)

    while True:
        # Lệnh JS: Kéo thanh cuộn xuống vị trí thấp nhất hiện tại
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", scroll_div)

        # Chờ loading (quan trọng: Google Maps cần thời gian để fetch API review cũ)
        time.sleep(1.5)

        # Tính lại chiều cao sau khi cuộn
        new_height = driver.execute_script(
            "return arguments[0].scrollHeight", scroll_div)

        # Kiểm tra điều kiện dừng
        if new_height == last_height:
            # Thử chờ thêm chút nữa cho chắc (phòng mạng lag)
            time.sleep(2)
            new_height = driver.execute_script(
                "return arguments[0].scrollHeight", scroll_div)
            if new_height == last_height:
                print(">>> Đã đến cuối danh sách (No more reviews).")
                break

        # Cập nhật chiều cao mới để so sánh vòng sau
        last_height = new_height
        print(f"    ... Đang cuộn (Height: {last_height})")

# --- Cách sử dụng trong code chính ---
# (Giả sử bạn đang ở trong hàm scrape hoặc task)
# driver.get("link_google_map_cua_ban")
# open_and_scroll_to_bottom(driver)
