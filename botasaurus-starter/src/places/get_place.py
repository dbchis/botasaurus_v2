from datetime import datetime
import logging
import re
from src.places.clean_text import clean_text
from botasaurus.browser import Driver
from src.places.scrape_reviews import scrape_reviews
from src.places.scrape_menus import scrape_menus
from src.places.extract_lat_lng_from_url import extract_lat_lng_from_url


def get_place(driver: Driver):
    data = []
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

    # location = ""
    # try:
    #     elements = driver.select_all('div.Io6YTe')
    #     for el in elements:
    #         text = el.text.strip()
    #         if "+" in text and len(text) <= 50:
    #             location = clean_text(text)
    #             break
    # except Exception as e:
    #     logging.warning(f"Lỗi khi lấy Plus Code: {e}")
    lat, lng = extract_lat_lng_from_url(driver.current_url)
    location = {
        "Latitude": lat,
        "Longitude": lng
    }
    # location = {
    #     "Latitude": 10.7819979,
    #     "Longitude": 106.6986412
    # }

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
    reviews_text = clean_text(driver.get_text(
        'span[aria-label*="reviews"]') or "")  # Sửa R -> r
    reviews_count = ""
    if reviews_text:
        # reviews_text bây giờ là "(98)"
        match = re.search(r'([\d,.]+)', reviews_text)
        if match:
            # match.group(1) là "98"
            reviews_count = match.group(1).replace(
                ',', '').replace('.', '')
    hours = ""
    try:
        hours_selector = 'div[aria-expanded][role="button"] span.ZDu9vd'
        if driver.select(hours_selector):
            hours = clean_text(driver.get_text(hours_selector))
    except Exception:
        pass

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
    all_reviews_data = []
    if name:  # Chỉ chạy nếu lấy được tên
        all_reviews_data = scrape_reviews(driver, name)
    menu_data = []
    if name:
        menu_data = scrape_menus(driver, name)
    working_hours = {
        "monday": [
            {"day_of_week": "monday", "slot": 1, "start_time": "10:00",
             "end_time": "14:00", "is_closed": False},
            {"day_of_week": "monday", "slot": 2, "start_time": "16:30",
             "end_time": "22:00", "is_closed": False}
        ],
        "tuesday": [
            {"day_of_week": "tuesday", "slot": 1, "start_time": "10:00",
             "end_time": "14:00", "is_closed": False},
            {"day_of_week": "tuesday", "slot": 2, "start_time": "16:30",
             "end_time": "22:00", "is_closed": False}
        ],
        "sunday": [
            {"day_of_week": "sunday", "slot": 1, "start_time": "00:00",
             "end_time": "00:00", "is_closed": True}
        ]
    }
    place_data = {
        "name": name,
        "created_at": now,
        "updated_at": now,
        "logo_url": image,
        "intro": category,
        "policy": None,
        "note": menu_data[0].get("description") if menu_data else None,
        "email": None,
        "address": address,
        "city": None,
        "county": None,
        "ward": None,
        "phone": phone,
        "google_map_link": driver.current_url,
        "rating": rating,
        # Số lượng review (đã làm sạch)
        "reviews_count": reviews_count,
        "type": category,
        "hours": hours,
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

    }

    if name:
        data.append(place_data)

    return data
