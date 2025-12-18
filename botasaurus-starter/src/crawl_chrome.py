
import logging
import botasaurus as bt
from botasaurus.browser import browser, Driver
import time
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@browser(
    block_images=True,     # Không cần ảnh cho description
    reuse_driver=True,     # Dùng chung driver nếu gọi song song
)
def get_description(driver: Driver, query: str):
    driver.get(
        f"https://www.google.com/search?q={query.replace(' ', '+')}+mô tả")
    time.sleep(2)

    try:
        driver.wait_for_element('div.WaaZC', wait=5)
        elements = driver.select_all('div.WaaZC span')
        description = ' '.join([el.text.strip()
                               for el in elements if el.text.strip()])
        return description
    except Exception as e:
        print(f"Lỗi khi lấy mô tả: {e}")
        return ""
