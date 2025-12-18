from botasaurus.browser import browser, Driver
import time
import logging
from src.places.get_place import get_place
from src.places.get_places import get_places

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@browser(
    block_images=False,
    parallel=10,
    # reuse_driver=True,
    reuse_driver=False,  # <--- ĐỔI THÀNH FALSE: Để đóng trình duyệt ngay khi xong việc
    close_on_crash=True,  # <--- THÊM: Đóng trình duyệt nếu code bị lỗi giữa chừng
)
def crawl_ggmap(driver: Driver, inputs: dict):
    # Mở link tìm kiếm Google Maps với từ khóa đã cho
    # query = f"{type} {street} {ward} {county} {city} {province} Việt Nam"
    query = f"Danh sách {inputs['type']} tại {inputs['street']} {inputs['ward']} {inputs['county']} {inputs['city']} {inputs['province']} Việt Nam"
    data = []
    search_url = f"https://www.google.com/maps/search/{query}"
    driver.google_get(search_url)
    time.sleep(1)
    links = set()  # Tập hợp các link địa điểm thu thập được
    if driver.select('h1.DUwDvf'):
        logging.info(
            f"[{query}] type = place")
        data = get_place(driver)
    else:
        logging.info(
            f"[{query}] type = list_place")
        data = get_places(driver, links, query, inputs)
    return data
