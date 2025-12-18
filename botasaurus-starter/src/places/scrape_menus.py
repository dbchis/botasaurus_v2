import logging
import re
import time
from botasaurus.browser import Driver
from typing import Any, Dict, List, Set
from src.places.clean_text import clean_text
from src.places.clean_image_url import clean_image_url


# def scrape_menus(driver: Driver, name_for_logging: str) -> List[Dict[str, Any]]:
#     """
#     Cào tất cả các món trong menu, dựa trên logic cuộn của scrape_all_reviews.
#     Hàm này sẽ cào cả menu dạng ảnh (K4UgGe) và menu dạng text (KoY8Lc),
#     sử dụng tên món ăn để chống trùng lặp.
#     """
#     all_menu_items = []
#     # Dùng tên món ăn đã chuẩn hóa để chống trùng lặp
#     scraped_item_names: Set[str] = set()

#     try:
#         # 1. Nhấn vào tab "Menu"
#         menu_tab_selector = 'button[aria-label*="Menu"][role="tab"]'
#         if driver.select(menu_tab_selector):
#             logging.info(f"[{name_for_logging}] Clicking 'Menu' tab...")
#             driver.click(menu_tab_selector)
#             time.sleep(1.5)  # Chờ menu tải
#     except Exception as e:
#         logging.warning(
#             f"[{name_for_logging}] Could not click Menu tab (maybe not needed): {e}")

#     # 2. Xác định bảng điều khiển để cuộn
#     scroll_panel_selector = 'div.m6QErb'  # Selector phổ biến
#     if not driver.select(scroll_panel_selector):
#         scroll_panel_selector = 'div[role="main"]'  # Fallback

#     # 3. Biến cho logic cuộn
#     last_item_count = -1
#     stagnant_scrolls = 0
#     max_stagnant_scrolls = 1  # Tương tự như hàm review

#     logging.info(f"[{name_for_logging}] Starting menu scroll...")
#     while stagnant_scrolls < max_stagnant_scrolls:

#         new_items_found_in_pass = False

#         # --- 4. Cào Menu dạng Ảnh (dựa trên snippet <button class="K4UgGe">) ---
#         photo_item_elements = driver.select_all('button.K4UgGe')
#         for el in photo_item_elements:
#             try:
#                 # Dùng aria-label làm tên
#                 item_name = clean_text(el.get_attribute('aria-label'))
#                 if not item_name or item_name in scraped_item_names:
#                     continue  # Bỏ qua nếu không có tên hoặc đã cào

#                 scraped_item_names.add(item_name)
#                 new_items_found_in_pass = True

#                 item_image = None
#                 img_el = el.select('img.DaSXdd')
#                 if img_el:
#                     item_image = re.sub(
#                         r"=w\d+-h\d+-k-no.*$", "", img_el.get_attribute('src'))

#                 all_menu_items.append({
#                     "name": item_name,
#                     "price": None,  # Thường không có giá trong menu ảnh
#                     "image": item_image,
#                     "description": None,
#                     "source_type": "photo_menu"
#                 })
#             except Exception as e:
#                 logging.warning(
#                     f"[{name_for_logging}] Error parsing photo menu item: {e}")

#         # --- 5. Cào Menu dạng Text (dựa trên snippet <div class="KoY8Lc">) ---
#         text_item_elements = driver.select_all('div.KoY8Lc')
#         for el in text_item_elements:
#             try:
#                 name_el = el.select('span.zaTlhd')
#                 if not name_el:
#                     continue  # Bỏ qua nếu không tìm thấy tên

#                 item_name = clean_text(name_el.text)
#                 if not item_name or item_name in scraped_item_names:
#                     # Bỏ qua nếu không có tên hoặc đã cào (từ menu ảnh)
#                     continue

#                 scraped_item_names.add(item_name)
#                 new_items_found_in_pass = True

#                 # Lấy giá từ class 'cf6Bdb'
#                 price_el = el.select('div.cf6Bdb')
#                 item_price = clean_text(
#                     price_el.text) if price_el and price_el.text else None

#                 # Bạn có thể mở rộng để cào mô tả (thường là class khác)
#                 # desc_el = el.select('span.Y0A0v') # Ví dụ, cần kiểm tra class
#                 # item_desc = clean_text(desc_el.text) if desc_el else None

#                 all_menu_items.append({
#                     "name": item_name,
#                     "price": item_price,
#                     "image": None,  # Thường không có ảnh trong menu text
#                     "description": None,  # Thêm logic cào mô tả ở đây
#                     "source_type": "text_menu"
#                 })
#             except Exception as e:
#                 logging.warning(
#                     f"[{name_for_logging}] Error parsing text menu item: {e}")

#         # --- 6. Kiểm tra điều kiện dừng (logic từ hàm review) ---
#         current_item_count = len(scraped_item_names)

#         if not new_items_found_in_pass and current_item_count > 0:
#             # Nếu cuộn 1 vòng mà không tìm thấy tên món mới nào
#             stagnant_scrolls += 1
#             logging.info(
#                 f"[{name_for_logging}] No new menu items. Stagnant: {stagnant_scrolls}/{max_stagnant_scrolls}")
#         elif current_item_count == last_item_count:
#             # Fallback nếu logic trên sai
#             stagnant_scrolls += 1
#             logging.info(
#                 f"[{name_for_logging}] Item count unchanged. Stagnant: {stagnant_scrolls}/{max_stagnant_scrolls}")
#         else:
#             stagnant_scrolls = 0  # Reset
#             last_item_count = current_item_count
#             logging.info(
#                 f"[{name_for_logging}] Found {current_item_count} menu items so far...")

#         if stagnant_scrolls >= max_stagnant_scrolls:
#             logging.info(
#                 f"[{name_for_logging}] Reached max stagnant scrolls. Stopping menu scrape.")
#             break

#         # --- 7. Cuộn bảng menu ---
#         try:
#             driver.scroll(scroll_panel_selector)
#             time.sleep(0.3)  # Chờ tải thêm món
#         except Exception as scroll_e:
#             logging.warning(
#                 f"[{name_for_logging}] Could not scroll menu panel, stopping: {scroll_e}")
#             break  # Dừng nếu không cuộn được

#     logging.info(
#         f"[{name_for_logging}] Scraped total {len(all_menu_items)} menu items.")
#     return all_menu_items

# v2
def scrape_menus(driver: Driver, name_for_logging: str) -> List[Dict[str, Any]]:
    logging.info(f"[{name_for_logging}] Scraping menus...")

    all_items = []
    seen_names: Set[str] = set()

    # ==== CLICK TAB MENU (ỔN ĐỊNH) ===================================
    menu_selectors = [
        'button[aria-label*="Menu"][role="tab"]',
        'button[jsname="GzZ4Hf"]',
        'div[role="tab"]:has(span:contains("Menu"))'
    ]

    clicked = False
    for selector in menu_selectors:
        try:
            if driver.select(selector):
                driver.click(selector)
                clicked = True
                logging.info(
                    f"[{name_for_logging}] Clicked Menu via {selector}")
                break
        except:
            continue

    time.sleep(1.2)

    # ==== PANEL SCROLL (ỔN ĐỊNH) =====================================
    scroll_panel = None
    for sel in ['div.m6QErb', 'div[role="main"]', 'div.scrollable', 'div.section-scrollbox']:
        if driver.select(sel):
            scroll_panel = sel
            break

    if not scroll_panel:
        logging.warning(f"[{name_for_logging}] No scroll panel found — abort")
        return all_items

    logging.info(f"[{name_for_logging}] Using scroll panel: {scroll_panel}")

    last_count = 0
    stagnant = 0
    max_stagnant = 8   # Quan trọng: cho phép scroll sâu hơn

    # ==== LOOP CUỘN MENU ============================================
    while stagnant < max_stagnant:

        found_new = False

        # ---- MENU DẠNG ẢNH ------------------------------------------
        photo_items = driver.select_all('button.K4UgGe')
        for el in photo_items:
            try:
                name = clean_text(el.get_attribute("aria-label") or "")
                if not name or name in seen_names:
                    continue

                seen_names.add(name)
                found_new = True

                img_el = el.select("img")
                image_url = None
                if img_el:
                    src = img_el.get_attribute("src")
                    if src:
                        # image_url = re.sub(r"=w\d+-h\d+-k-no.*$", "", src)
                        image_url = clean_image_url(src)

                all_items.append({
                    "name": name,
                    "price": None,
                    "image": image_url,
                    "description": None,
                    "source_type": "photo_menu",
                })
            except:
                continue

        # ---- MENU DẠNG TEXT -----------------------------------------
        text_items = driver.select_all("div.KoY8Lc")
        for el in text_items:
            try:
                name_el = el.select("span.zaTlhd")
                if not name_el:
                    continue

                name = clean_text(name_el.text)
                if not name or name in seen_names:
                    continue

                seen_names.add(name)
                found_new = True

                price_el = el.select("div.cf6Bdb")
                price = clean_text(price_el.text) if price_el else None

                all_items.append({
                    "name": name,
                    "price": price,
                    "image": None,
                    "description": None,
                    "source_type": "text_menu",
                })
            except:
                continue

        # ==== LOGIC DỪNG =============================================
        if found_new:
            stagnant = 0
        else:
            stagnant += 1

        logging.info(
            f"[{name_for_logging}] Menu count: {len(seen_names)} (stagnant={stagnant}/{max_stagnant})")

        # ==== SCROLL MẠNH ============================================
        try:
            driver.scroll(scroll_panel, amount=2000)  # Scroll mạnh để load xa
            time.sleep(0.5)
        except:
            break

    logging.info(f"[{name_for_logging}] FINAL MENU COUNT = {len(all_items)}")
    return all_items
