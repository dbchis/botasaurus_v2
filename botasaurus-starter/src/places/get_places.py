from datetime import datetime
import logging
import re
import time
from src.places.clean_text import clean_text
from botasaurus.browser import Driver
from src.places.scrape_reviews import scrape_reviews
from src.places.scrape_menus import scrape_menus
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.places.extract_lat_lng_from_url import extract_lat_lng_from_url
from src.places.working_hours.get_working_hours import get_working_hours
from src.places.clean_address import clean_address
from src.places.remove_vietnamese_accents import remove_vietnamese_accents
import threading
from src.places.clean_image_url import clean_image_url


def scrape_link(link, inputs: dict):
    driver = None
    try:
        driver = Driver(headless=True)
        # Mỗi thread tạo 1 driver riêng (không dùng driver chung!)
        driver.get(link)
        time.sleep(1)
        place_data = {}

        # # --- Lấy các trường dữ liệu ---

        name = clean_text(driver.get_text(
            "h1") if driver.select("h1") else "")

        phone = ""
        for selector in [
            'button[data-tooltip="Copy phone number"]',
            'button[data-item-id="phone"]',
        ]:
            if driver.select(selector):
                phone = clean_text(driver.get_text(selector))
                if phone:
                    break

        rating = ""
        for selector in [".F7nice span", 'span[aria-label*="stars"]']:
            if driver.select(selector):
                rating = clean_text(driver.get_text(selector))
                if rating:
                    break

        # location = []
        lat, lng = extract_lat_lng_from_url(link)
        location = {
            "Latitude": lat,
            "Longitude": lng
        }

        website = ""
        try:
            # Trang chi tiết dùng data-item-id="website"
            website_el = driver.select(
                'button[data-item-id="website"]')
            if website_el:
                website = clean_text(website_el.get_text())
            else:  # Fallback cho logic cũ
                website_button = driver.select(
                    'button[aria-label*="More info"]')
                if website_button:
                    website_button.click()
                    time.sleep(1)
                    website_element = driver.select('a[href*="http"]')
                    if website_element:
                        website = clean_text(
                            website_element.get_attribute("href"))
        except Exception:
            pass

        image = ""
        img_selectors = [
            'img[src*="googleusercontent"]',
            'img[src*="maps.gstatic.com"]',
        ]
        for selector in img_selectors:
            img_tag = driver.select(selector)
            if img_tag:
                img_link = img_tag.get_attribute("src")
                if img_link and "googleusercontent.com" in img_link:
                    image = re.sub(r"=w\d+-h\d+-k-no.*$", "", img_link)
                    break

        address = clean_text(
            driver.get_text('button[data-item-id="address"]') or ""
        )
        reviews_text = ""
        # Lấy SỐ LƯỢNG review (text) và làm sạch
        # reviews_text = clean_text(driver.get_text(
        #     'span[aria-label*="reviews"]') or "")  # Sửa R -> r
        reviews_count = ""
        if reviews_text:
            # reviews_text bây giờ là "(98)"
            match = re.search(r'([\d,.]+)', reviews_text)
            if match:
                # match.group(1) là "98"
                reviews_count = match.group(1).replace(
                    ',', '').replace('.', '')

        working_hours = get_working_hours(driver)

        category = ""
        for selector in ['.DkEaL', 'button[jsaction="pane.wfvdle235.category"]']:
            if driver.select(selector):
                category = clean_text(driver.get_text(selector))
                if category:
                    break

        price_range = ""
        try:
            # ---- THAY ĐỔI LỚN ----
            # Tìm TẤT CẢ các span.mgr77e trên trang
            # Đây là selector ổn định nhất qua tất cả các ví dụ của bạn
            potential_price_spans = driver.select_all('span.mgr77e')

            if not potential_price_spans:
                # print("Không tìm thấy span.mgr77e nào") # Bật để gỡ lỗi
                pass

            # Duyệt qua từng span đã tìm thấy
            for span in potential_price_spans:
                text = span.text.strip()  # Ví dụ text có thể là: "·₫200–300K"

                # Kiểm tra xem span này có chứa ký hiệu tiền tệ không
                if '₫' in text or '$' in text:
                    price_range = clean_text(text)

                    # Đã tìm thấy giá trị mong muốn, thoát ngay lập tức
                    break

            # Với cách này, chúng ta không cần "Cách 2 (Regex)" dự phòng nữa
            # vì chúng ta đã nhắm thẳng vào phần tử chứa text.

        except Exception as e:
            # print(f"Lỗi khi tìm price_range: {e}") # Bật lên để gỡ lỗi
            pass

        # print(f"Giá tìm được: {price_range}") # Bật lên để gỡ lỗi

        amenities = []

        try:
            # 'LTs0Rc' là class cho mỗi mục tiện ích/dịch vụ riêng lẻ
            amenity_elements = driver.select_all('div.LTs0Rc')

            if amenity_elements:
                amenities = [clean_text(el.get_attribute('aria-label'))
                             for el in amenity_elements
                             if el.get_attribute('aria-label')]  # Lấy 'aria-label'

                # Loại bỏ các giá trị None hoặc rỗng nếu có
                amenities = [item for item in amenities if item]

        except Exception as e:
            # Nên log lỗi để biết nếu có vấn đề
            # logging.warning(f"Error scraping amenities: {e}")
            pass

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # --- Gọi hàm cào tất cả review ---
        time.sleep(1)
        all_reviews_data = []
        if name:  # Chỉ chạy nếu lấy được tên
            all_reviews_data = scrape_reviews(driver, name)
        menu_data = []
        if name:
            menu_data = scrape_menus(driver, name)

        if inputs['city']:
            city = inputs['city']
        else:
            if inputs['province']:
                city = inputs['province']
            else:
                city = None
        policy = f"Khách hàng vui lòng liên hệ {phone} để biết thêm chi tiết về chính sách của {name}."
        note = f"Đang cập nhật..."
        # note = (
        #     f'Thông tin thêm về {name} có thể được tìm thấy trên '
        #     f'<a href="{website}" target="_blank" rel="noopener noreferrer">'
        #     f'trang web chính thức</a>'
        # )

        email = "booking@tripc.ai"
        intro = ", ".join(amenities)
        disadvantages = "Đang cập nhật ...."
        advantages = "Đang cập nhật ...."
        province = remove_vietnamese_accents(city) if city else None

        place_data = {
            "name": name,
            "created_at": now,
            "updated_at": now,
            "logo_url": clean_image_url(image),
            "cover_image_url": clean_image_url(image),
            "intro": intro,
            "policy": policy,
            "note": note,
            "email": email,
            "address": clean_address(address),
            "city": city,
            "province": province,
            "county": inputs['county'] if inputs['county'] else None,
            "ward": inputs['ward'] if inputs['ward'] else None,
            "phone": phone,
            "google_map_link": link,
            "rating": rating,
            "reviews_count": reviews_count,  # Số lượng review (đã làm sạch)
            "type": inputs['type'],
            "price_range": price_range,
            "amenities": amenities,
            "location": location,
            "website": website,
            "images": menu_data,
            "reviews": all_reviews_data,
            "otas": None,
            "licenses": None,
            # "supplier_id": None,
            "deleted_at": None,
            "working_hours": working_hours,
            "disadvantages": disadvantages,
            "advantages": advantages,

        }
        return place_data
    except Exception as e:
        logging.error(f"Lỗi khi scrape {link}: {e}")
        return None
    finally:
        # Khối 'finally' này RẤT QUAN TRỌNG
        # Nó đảm bảo driver được đóng để giải phóng tài nguyên
        if driver:
            driver.close()


# def get_places(driver: Driver, links: set, query: str, inputs: dict):
#     last_count = -1  # Số lượng link ở lần lặp trước
#     same_count_times = 0  # Đếm số vòng lặp không có thêm link mới
#     max_same_count = 1  # Dừng sau 1 lần không có link mới (Giữ nguyên)
#     numResult = inputs['numResult']

#     # 1. SỬ DỤNG numResult TRONG VÒNG LẶP WHILE
#     # Vòng lặp sẽ tiếp tục miễn là:
#     # - Chưa bị kẹt (same_count_times < max_same_count)
#     # - VÀ số lượng link tìm thấy (len(links)) CÒN ÍT HƠN numResult
#     while same_count_times < max_same_count and len(links) < numResult:
#         place_elements = driver.select_all('a[href*="place"]')
#         new_links = {el.get_attribute("href") for el in place_elements}
#         links.update(new_links)

#         if len(links) == last_count:
#             same_count_times += 1
#         else:
#             same_count_times = 0
#             last_count = len(links)

#         # Nếu đã tìm đủ link, không cần cuộn hoặc click "More" nữa
#         if len(links) >= numResult:
#             break

#         scroll_selector = 'div[aria-label^="Results for"]'
#         if not driver.select(scroll_selector):
#             scroll_selector = ".m6QErb"  # fallback
#         try:
#             driver.scroll(scroll_selector)
#         except Exception:
#             logging.warning("Could not scroll results list. Stopping.")
#             break
#         time.sleep(0.5)

#         more_results = driver.select(
#             'div[role="button"][aria-label*="More results"]')
#         if more_results:
#             try:
#                 more_results.click()
#                 time.sleep(0.5)
#             except Exception:
#                 break

#     # 2. GIỚI HẠN SỐ LƯỢNG LINK SẼ CÀO
#     # Chuyển set 'links' thành list và chỉ lấy số lượng bằng numResult
#     links_to_crawl = list(links)[:numResult]

#     logging.info(
#         f"[{query}] Found {len(links)} total links. Crawling {len(links_to_crawl)}.")
#     data = []  # Danh sách dữ liệu địa điểm
#     # 3. TRUY CẬP TỪNG LINK (ĐÃ ĐƯỢC GIỚI HẠN)
#     with ThreadPoolExecutor(max_workers=5) as executor:
#         # Chỉ submit 'links_to_crawl' thay vì 'links'
#         future_to_link = {executor.submit(
#             scrape_link, link, inputs): link for link in links_to_crawl}

#         for future in as_completed(future_to_link):
#             result = future.result()
#             if result:
#                 result['total'] = len(links_to_crawl)
#                 result['query'] = query
#                 data.append(result)
#     return data

# v2
def scrape_worker_wrapper(link, inputs, index, total_count):
    """
    Hàm wrapper: In log + Gán ID cho kết quả
    """
    worker_name = threading.current_thread().name
    print(f"[{worker_name}] ⏳ Processing {index}/{total_count}: {link}")

    # 1. Gọi hàm scrape gốc
    result = scrape_link(link, inputs)

    # 2. Nếu có kết quả, gán luôn ID vào dict
    if result:
        result['id'] = index  # <--- THÊM ID TẠI ĐÂY

    return result


def get_places(driver, links: set, query: str, inputs: dict):
    last_count = -1
    same_count_times = 0
    max_same_count = 1
    numResult = inputs['numResult']

    logging.info(f"[{query}] Start scrolling to find places...")

    # --- 1. SCROLL & LẤY LINK (GIỮ NGUYÊN) ---
    while same_count_times < max_same_count and len(links) < numResult:
        place_elements = driver.select_all('a[href*="place"]')
        new_links = {el.get_attribute("href") for el in place_elements}
        links.update(new_links)

        if len(links) == last_count:
            same_count_times += 1
        else:
            same_count_times = 0
            last_count = len(links)

        if len(links) >= numResult:
            break

        scroll_selector = 'div[aria-label^="Results for"]'
        if not driver.select(scroll_selector):
            scroll_selector = ".m6QErb"

        try:
            driver.scroll(scroll_selector)
        except Exception:
            logging.warning("Could not scroll results list. Stopping.")
            break
        time.sleep(0.5)

        more_results = driver.select(
            'div[role="button"][aria-label*="More results"]')
        if more_results:
            try:
                more_results.click()
                time.sleep(0.5)
            except Exception:
                break

    # --- 2. CHUẨN BỊ ---
    links_to_crawl = list(links)[:numResult]
    total_links = len(links_to_crawl)

    logging.info(
        f"[{query}] Found {len(links)} total links. Crawling {total_links}.")

    data = []

    # --- 3. ĐA LUỒNG ---
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Truyền index (idx) vào wrapper để làm ID
        future_to_link = {
            executor.submit(scrape_worker_wrapper, link, inputs, idx, total_links): link
            for idx, link in enumerate(links_to_crawl, 1)  # Bắt đầu đếm từ 1
        }

        for future in as_completed(future_to_link):
            try:
                result = future.result()
                if result:
                    data.append(result)
            except Exception as e:
                logging.error(f"Error scraping a link: {e}")

    # --- 4. SẮP XẾP LẠI THEO ID TĂNG DẦN ---
    # Do chạy đa luồng, thứ tự append vào list sẽ lộn xộn (VD: id 5 xong trước id 1).
    # Cần sort lại để JSON đầu ra theo thứ tự 1, 2, 3...
    if data:
        data.sort(key=lambda x: x['id'])

    return data
