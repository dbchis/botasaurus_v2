# import logging
# from botasaurus.browser import Driver
# import time
# import re
# from src.places.clean_text import clean_text


# def scrape_reviews(driver: Driver, name_for_logging: str):
#     """
#     Nâng cấp để cào tất cả review, bao gồm cả thông tin tác giả,
#     ảnh đại diện, link profile, ảnh review, và lượt thích.
#     """
#     all_reviews_data = []
#     scraped_review_ids = set()  # Để theo dõi các review đã cào, tránh trùng lặp
#     try:
#         review_tab_selector = 'button[aria-label*="Reviews"][role="tab"]'
#         if driver.select(review_tab_selector):
#             logging.info(f"[{name_for_logging}] Clicking 'Reviews' tab...")
#             driver.click(review_tab_selector)
#             time.sleep(1.5)  # Chờ review tải
#     except Exception as e:
#         logging.warning(
#             f"[{name_for_logging}] Could not click Reviews tab (maybe not needed): {e}")

#     scroll_panel_selector = 'div.m6QErb'  # Selector phổ biến cho bảng này
#     if not driver.select(scroll_panel_selector):
#         scroll_panel_selector = 'div[role="main"]'  # Fallback

#     last_review_count = -1
#     stagnant_scrolls = 0
#     # Tăng giới hạn này nếu bạn muốn cuộn nhiều hơn
#     max_stagnant_scrolls = 1

#     logging.info(f"[{name_for_logging}] Starting review scroll...")
#     while stagnant_scrolls < max_stagnant_scrolls:
#         # Selector chính cho mỗi khối review
#         review_elements = driver.select_all('div.jftiEf')

#         if not review_elements and last_review_count == -1:
#             logging.warning(
#                 f"[{name_for_logging}] No review elements found on init. Stopping.")
#             break  # Không tìm thấy review nào ngay từ đầu

#         new_reviews_found_in_pass = False
#         for el in review_elements:
#             try:
#                 # 1. Sử dụng data-review-id để chống trùng lặp
#                 review_id = el.get_attribute('data-review-id')
#                 if not review_id or review_id in scraped_review_ids:
#                     continue  # Bỏ qua nếu không có ID hoặc đã cào rồi

#                 scraped_review_ids.add(review_id)
#                 new_reviews_found_in_pass = True

#                 # --- Trích xuất dữ liệu tác giả (Nâng cấp) ---
#                 author_el = el.select('div.d4r55')
#                 author_name = clean_text(
#                     author_el.text) if author_el else "N/A"

#                 info_el = el.select('div.RfnDt')
#                 author_info = clean_text(info_el.text) if info_el else None

#                 avatar_el = el.select('img.NBa7we')
#                 author_avatar = avatar_el.get_attribute(
#                     'src') if avatar_el else None
#                 _author_avatar = re.sub(
#                     r"=w\d+-h\d+-k-no.*$", "", author_avatar)

#                 link_el = el.select('button.al6Kxe')
#                 author_link = link_el.get_attribute(
#                     'data-href') if link_el else None

#                 # --- Trích xuất dữ liệu review (Nâng cấp) ---
#                 rating_el = el.select('span.kvMYJc[role="img"]')
#                 review_rating = rating_el.get_attribute(
#                     'aria-label') if rating_el else "N/A"

#                 date_el = el.select('span.rsqaWe')
#                 review_date = clean_text(date_el.text) if date_el else "N/A"

#                 # Lấy nội dung text và xử lý nút "Thêm" (More) - Logic cũ vẫn tốt
#                 text_content = ""
#                 text_el = el.select('span.wiI7pd')
#                 if text_el:
#                     more_button = el.select('button.w8nwRe')
#                     if more_button:
#                         try:
#                             more_button.click()  # Nhấn để mở rộng text
#                             # Chờ text hiển thị (giảm thời gian)
#                             time.sleep(1)
#                             # Lấy lại text_el sau khi nhấn
#                             text_content = clean_text(
#                                 el.select('span.wiI7pd').text)
#                         except Exception:
#                             text_content = clean_text(text_el.text)  # Fallback
#                     else:
#                         text_content = clean_text(text_el.text)

#                 # --- Trích xuất ảnh trong review (Mới) ---
#                 image_els = el.select_all('button.Tya61d')
#                 review_images = []
#                 for img_el in image_els:
#                     style = img_el.get_attribute('style')
#                     if style:
#                         # Dùng regex để trích xuất URL từ 'background-image: url("...")'
#                         match = re.search(r'url\("?([^")]+)"?\)', style)
#                         _match = re.sub(r"=w\d+-h\d+-k-no.*$", "", match)
#                         if match:
#                             review_images.append(_match.group(1))

#                 # --- Trích xuất lượt thích (Mới) ---
#                 likes_el = el.select(
#                     'button.gllhef[aria-label*="Thích"] span.NlVald')
#                 # Lấy text, có thể là "Thích" hoặc một con số
#                 likes_text = clean_text(likes_el.text) if likes_el else "0"

#                 all_reviews_data.append({
#                     "review_id": review_id,
#                     "author_name": author_name,
#                     "author_info": author_info,
#                     "author_avatar": _author_avatar,
#                     "author_link": author_link,
#                     "rating": review_rating,
#                     "date": review_date,
#                     "content": text_content,
#                     "images": review_images,  # Danh sách ảnh
#                     "likes": likes_text
#                 })

#             except Exception as review_e:
#                 logging.warning(
#                     f"Error parsing one review ({review_id}): {review_e}")

#         # 7. Kiểm tra điều kiện dừng (Cải tiến)
#         current_review_count = len(scraped_review_ids)
#         if not new_reviews_found_in_pass and current_review_count > 0:
#             # Nếu cuộn 1 vòng mà không tìm thấy review ID mới nào
#             stagnant_scrolls += 1
#             logging.info(
#                 f"[{name_for_logging}] No new reviews. Stagnant: {stagnant_scrolls}/{max_stagnant_scrolls}")
#         elif current_review_count == last_review_count:
#             # Fallback nếu logic trên sai, vẫn giữ cách đếm cũ
#             stagnant_scrolls += 1
#             logging.info(
#                 f"[{name_for_logging}] Review count unchanged. Stagnant: {stagnant_scrolls}/{max_stagnant_scrolls}")
#         else:
#             stagnant_scrolls = 0  # Reset
#             last_review_count = current_review_count
#             logging.info(
#                 f"[{name_for_logging}] Found {current_review_count} reviews so far...")

#         if stagnant_scrolls >= max_stagnant_scrolls:
#             logging.info(
#                 f"[{name_for_logging}] Reached max stagnant scrolls. Stopping.")
#             break

#         # 8. Cuộn bảng review
#         try:
#             driver.scroll(scroll_panel_selector)
#             time.sleep(0.5)  # Tăng nhẹ thời gian chờ sau khi cuộn
#         except Exception as scroll_e:
#             logging.warning(
#                 f"Could not scroll review panel, stopping: {scroll_e}")
#             break  # Dừng nếu không cuộn được

#     logging.info(
#         f"[{name_for_logging}] Scraped total {len(all_reviews_data)} reviews.")
#     return all_reviews_data

# v2
# import logging
# import time
# import re
# from botasaurus.browser import Driver
# from src.places.clean_text import clean_text


# def _parse_single_review(el, driver: Driver) -> dict:
#     """
#     Hàm phụ trợ: Giữ nguyên như cũ.
#     """
#     try:
#         author_el = el.select('div.d4r55')
#         author_name = clean_text(author_el.text) if author_el else "N/A"

#         info_el = el.select('div.RfnDt')
#         author_info = clean_text(info_el.text) if info_el else None

#         avatar_el = el.select('img.NBa7we')
#         author_avatar = avatar_el.get_attribute('src') if avatar_el else None
#         if author_avatar:
#             author_avatar = re.sub(r"=w\d+-h\d+-k-no.*$", "", author_avatar)

#         link_el = el.select('button.al6Kxe')
#         author_link = link_el.get_attribute('data-href') if link_el else None

#         rating_el = el.select('span.kvMYJc[role="img"]')
#         review_rating = rating_el.get_attribute(
#             'aria-label') if rating_el else "N/A"

#         date_el = el.select('span.rsqaWe')
#         review_date = clean_text(date_el.text) if date_el else "N/A"

#         text_content = ""
#         text_el = el.select('span.wiI7pd')

#         if text_el:
#             more_button = el.select('button.w8nwRe')
#             if more_button:
#                 try:
#                     driver.run_js(
#                         "arguments[0].click();", more_button._element)
#                     time.sleep(0.1)
#                     text_content = clean_text(el.select('span.wiI7pd').text)
#                 except Exception:
#                     text_content = clean_text(text_el.text)
#             else:
#                 text_content = clean_text(text_el.text)

#         image_els = el.select_all('button.Tya61d')
#         review_images = []
#         for img_el in image_els:
#             style = img_el.get_attribute('style')
#             if style:
#                 match = re.search(r'url\("?([^")]+)"?\)', style)
#                 if match:
#                     raw_url = match.group(1)
#                     clean_url = re.sub(r"=w\d+-h\d+-k-no.*$", "", raw_url)
#                     review_images.append(clean_url)

#         likes_el = el.select('button.gllhef[aria-label*="Thích"] span.NlVald')
#         likes_text = clean_text(likes_el.text) if likes_el else "0"

#         return {
#             "author_name": author_name,
#             "author_info": author_info,
#             "author_avatar": author_avatar,
#             "author_link": author_link,
#             "rating": review_rating,
#             "date": review_date,
#             "content": text_content,
#             "images": review_images,
#             "likes": likes_text
#         }
#     except Exception:
#         return None


# def scrape_reviews(driver: Driver, name_for_logging: str):
#     """
#     Sử dụng data-tab-index thay vì aria-label để tìm tab Reviews.
#     """
#     all_reviews_data = []
#     scraped_review_ids = set()

#     # --- 1. CHIẾN THUẬT TÌM TAB MỚI (KHÔNG CẦN LABEL) ---
#     logging.info(f"[{name_for_logging}] Finding Reviews tab by index...")

#     tab_found = False
#     # Thử index "1" (thường là Reviews) rồi đến "2" (dự phòng cho nhà hàng có Menu)
#     # data-tab-index trên Google Maps thường bắt đầu từ 0 (Overview)
#     potential_indexes = ["1", "2"]

#     for idx in potential_indexes:
#         # Selector chỉ dựa vào index, không quan tâm ngôn ngữ
#         tab_selector = f'button[role="tab"][data-tab-index="{idx}"]'

#         if driver.select(tab_selector):
#             logging.info(f"[{name_for_logging}] Trying tab index {idx}...")
#             driver.click(tab_selector)
#             time.sleep(2.5)  # Chờ load

#             # KIỂM TRA: Sau khi click, có thấy dấu hiệu của review không?
#             # 1. Có thẻ review (div.jftiEf) xuất hiện?
#             # 2. Hoặc bảng cuộn review (div.m6QErb) xuất hiện?
#             if driver.select('div.jftiEf') or driver.select('div.m6QErb'):
#                 logging.info(
#                     f"[{name_for_logging}] Tab {idx} looks like Reviews. Proceeding.")
#                 tab_found = True
#                 break
#             else:
#                 logging.warning(
#                     f"[{name_for_logging}] Tab {idx} clicked but no reviews found. Trying next...")

#     if not tab_found:
#         logging.warning(
#             f"[{name_for_logging}] Could not identify Reviews tab via index. Scrape might fail.")

#     # --- 2. XÁC ĐỊNH SELECTOR ĐỂ CUỘN ---
#     scroll_panel_selector = 'div.m6QErb:nth-of-type(2)'
#     if not driver.select(scroll_panel_selector):
#         scroll_panel_selector = 'div.m6QErb'
#         if not driver.select(scroll_panel_selector):
#             scroll_panel_selector = 'div[role="main"]'

#     # --- 3. VÒNG LẶP CÀO & CUỘN (LOGIC GET_PLACES) ---
#     last_count = -1
#     same_count_times = 0
#     max_same_count = 3

#     # Nếu tab chưa mở đúng, có thể vòng lặp này sẽ kết thúc ngay lập tức (0 reviews)
#     while same_count_times < max_same_count:
#         # A. Lấy review elements
#         review_elements = driver.select_all('div.jftiEf')

#         new_items_in_pass = 0
#         for el in review_elements:
#             r_id = el.get_attribute('data-review-id')
#             if r_id and r_id not in scraped_review_ids:
#                 data = _parse_single_review(el, driver)
#                 if data:
#                     data['review_id'] = r_id
#                     all_reviews_data.append(data)
#                     scraped_review_ids.add(r_id)
#                     new_items_in_pass += 1

#         # B. Kiểm tra tiến độ
#         current_count = len(scraped_review_ids)

#         if current_count == last_count:
#             same_count_times += 1
#             logging.info(
#                 f"[{name_for_logging}] Stagnant: {same_count_times}/{max_same_count}")
#         else:
#             same_count_times = 0
#             last_count = current_count
#             logging.info(
#                 f"[{name_for_logging}] Collected {current_count} reviews (+{new_items_in_pass} new)...")

#         # C. Cuộn
#         try:
#             driver.scroll(scroll_panel_selector)
#             time.sleep(1.5)
#         except Exception:
#             break

#     logging.info(
#         f"[{name_for_logging}] DONE. Total reviews scraped: {len(all_reviews_data)}")
#     return all_reviews_data

# v3
import logging
from botasaurus.browser import Driver  # Đã xóa Element
import time
import re

# Giữ nguyên hàm clean_text


def clean_text(text):
    if not text:
        return ""
    return text.strip().replace('\n', ' ')


def scrape_reviews(driver: Driver, name_for_logging: str):
    all_reviews_data = []
    scraped_review_ids = set()

    # 1. Chuyển sang tab Reviews
    try:
        review_tab_selector = 'button[role="tab"][aria-label*="Reviews"], button[role="tab"][aria-label*="Bài đánh giá"]'
        if driver.is_element_present(review_tab_selector):
            logging.info(f"[{name_for_logging}] Clicking 'Reviews' tab...")
            driver.click(review_tab_selector)
            time.sleep(2)
    except Exception as e:
        logging.warning(f"[{name_for_logging}] Issue switching tabs: {e}")

    # 2. Đợi review container xuất hiện
    review_item_selector = 'div.jftiEf'
    try:
        # Nếu phiên bản botasaurus của bạn cũ và không có wait_for_element,
        # hãy dùng time.sleep(5) thay thế dòng dưới
        if hasattr(driver, 'wait_for_element'):
            driver.wait_for_element(review_item_selector, wait=10)
        else:
            time.sleep(5)
    except Exception:
        logging.warning(f"[{name_for_logging}] No reviews found (timeout).")
        return []

    max_stagnant_scrolls = 3
    stagnant_scrolls = 0

    logging.info(f"[{name_for_logging}] Starting scraping loop...")

    while stagnant_scrolls < max_stagnant_scrolls:
        # Lấy tất cả review hiện có
        review_elements = driver.select_all(review_item_selector)

        new_items_in_pass = 0

        for el in review_elements:
            try:
                # --- A. Lấy ID ---
                review_id = el.get_attribute('data-review-id')
                if not review_id or review_id in scraped_review_ids:
                    continue

                # --- B. Xử lý nút "More/Thêm" ---
                more_btn_selector = 'button.w8nwRe'
                if el.select(more_btn_selector):
                    try:
                        # Dùng run_js để click an toàn
                        driver.run_js(
                            "arguments[0].click();", el.select(more_btn_selector))
                        time.sleep(0.1)
                    except:
                        pass

                # --- C. Trích xuất dữ liệu ---

                # Tác giả & Avatar
                author_el = el.select('div.d4r55')
                author_name = clean_text(
                    author_el.text) if author_el else "N/A"

                avatar_el = el.select('img.NBa7we')
                author_avatar = avatar_el.get_attribute(
                    'src') if avatar_el else ""
                if author_avatar:
                    author_avatar = re.sub(r'=w\d+-h\d+.*$', '', author_avatar)

                info_el = el.select('div.RfnDt')
                author_info = clean_text(info_el.text) if info_el else ""

                link_el = el.select('button.al6Kxe')
                author_link = link_el.get_attribute(
                    'data-href') if link_el else ""

                # Rating & Date
                rating_el = el.select('span.kvMYJc')
                rating = rating_el.get_attribute(
                    'aria-label') if rating_el else "0"
                if rating:
                    rating_match = re.search(r'(\d+)', rating)
                    rating = rating_match.group(1) if rating_match else rating

                date_el = el.select('span.rsqaWe')
                review_date = clean_text(date_el.text) if date_el else ""

                # Nội dung
                content_el = el.select('span.wiI7pd')
                content = clean_text(content_el.text) if content_el else ""

                # Hình ảnh (Regex lấy từ style)
                images = []
                image_btns = el.select_all('button.Tya61d')
                for img_btn in image_btns:
                    style = img_btn.get_attribute('style')
                    if style:
                        match = re.search(r'url\("?([^")]+)"?\)', style)
                        if match:
                            img_url = match.group(1)
                            img_url = re.sub(r'=w\d+-h\d+.*$', '', img_url)
                            images.append(img_url)

                # Likes
                like_el = el.select('button.gllhef span.NlVald')
                likes = "0"
                if like_el:
                    like_text = clean_text(like_el.text)
                    if like_text.isdigit():
                        likes = like_text

                # Lưu data
                review_data = {
                    "review_id": review_id,
                    "author_name": author_name,
                    "author_info": author_info,
                    "rating": rating,
                    "date": review_date,
                    "content": content,
                    "images": images,
                    "likes": likes,
                    "author_avatar": author_avatar,
                    "author_link": author_link
                }

                all_reviews_data.append(review_data)
                scraped_review_ids.add(review_id)
                new_items_in_pass += 1

            except Exception:
                continue

        # --- Scroll Logic ---
        current_count = len(scraped_review_ids)
        logging.info(
            f"[{name_for_logging}] Scraped: {current_count} (+{new_items_in_pass} new)")

        if new_items_in_pass == 0:
            stagnant_scrolls += 1
        else:
            stagnant_scrolls = 0

        try:
            # Scroll bằng Javascript vào đúng container
            scroll_script = """
                var container = Array.from(document.querySelectorAll('div.m6QErb')).find(div => div.querySelector('div.jftiEf'));
                if (container) {
                    container.scrollTop += 2000;
                    return true;
                }
                return false;
            """
            scrolled = driver.run_js(scroll_script)

            if not scrolled:
                # Fallback: Ấn phím End nếu JS không tìm thấy container
                driver.type(driver.select('body'), "End")

            time.sleep(1.5)
        except Exception as e:
            logging.error(f"Scroll failed: {e}")
            break

    return all_reviews_data
