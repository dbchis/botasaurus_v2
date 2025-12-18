# import re
# from datetime import datetime


# def format_working_hours(raw_hours_list):
#     """
#     Chuyển đổi list string giờ làm việc sang cấu trúc JSON cho Backend Go.
#     Input ví dụ: ['Monday: 8:00 AM – 9:00 PM', 'Tuesday: Closed', ...]
#     """
#     if not raw_hours_list:
#         return None

#     # Khởi tạo map kết quả
#     week_map = {
#         "monday": [], "tuesday": [], "wednesday": [], "thursday": [],
#         "friday": [], "saturday": [], "sunday": []
#     }

#     # Map tên thứ từ Google Maps (Tiếng Anh) sang key của DTO
#     day_mapping = {
#         "monday": "monday", "mon": "monday",
#         "tuesday": "tuesday", "tue": "tuesday",
#         "wednesday": "wednesday", "wed": "wednesday",
#         "thursday": "thursday", "thu": "thursday",
#         "friday": "friday", "fri": "friday",
#         "saturday": "saturday", "sat": "saturday",
#         "sunday": "sunday", "sun": "sunday"
#     }

#     for item in raw_hours_list:
#         if not item:
#             continue

#         # Tách thứ và giờ (Ví dụ: "Monday: 09:00 - 17:00")
#         # Xử lý các ký tự lạ như – (en dash) thay vì -
#         clean_item = item.lower().replace('–', '-').replace('\u2009', ' ').strip()

#         found_day = None
#         for key, val in day_mapping.items():
#             if key in clean_item:
#                 found_day = val
#                 break

#         if not found_day:
#             continue

#         is_closed = "closed" in clean_item or "đóng cửa" in clean_item
#         start_time = "00:00"
#         end_time = "00:00"

#         if not is_closed:
#             if "24 hours" in clean_item or "cả ngày" in clean_item:
#                 start_time = "00:00"
#                 end_time = "23:59"  # Backend Go check start < end
#             else:
#                 # Regex tìm giờ (Hỗ trợ cả 12h AM/PM và 24h)
#                 # Tìm chuỗi dạng: 8:00 AM - 10:00 PM
#                 times = re.findall(
#                     r'(\d{1,2}:\d{2}\s?(?:am|pm)?)|(\d{1,2}\s?(?:am|pm))', clean_item)

#                 # Hàm phụ convert time text sang HH:MM 24h format
#                 def parse_time(t_str):
#                     t_str = t_str.strip()
#                     formats = ["%I:%M %p", "%I %p", "%H:%M", "%I:%M%p"]
#                     for fmt in formats:
#                         try:
#                             return datetime.strptime(t_str.upper(), fmt).strftime("%H:%M")
#                         except ValueError:
#                             continue
#                     return "00:00"

#                 # Flatten regex result và lọc chuỗi rỗng
#                 valid_times = [t[0] or t[1] for t in times if t[0] or t[1]]

#                 if len(valid_times) >= 2:
#                     start_time = parse_time(valid_times[0])
#                     end_time = parse_time(valid_times[1])

#         # Tạo object cho 1 slot (Mặc định slot 1)
#         slot_obj = {
#             "day_of_week": found_day,
#             "slot": 1,
#             "start_time": start_time,
#             "end_time": end_time,
#             "is_closed": is_closed
#         }

#         # Append vào đúng thứ trong tuần
#         week_map[found_day].append(slot_obj)

#     # Lọc bỏ các thứ không có dữ liệu (nếu cần) hoặc giữ nguyên cấu trúc rỗng
#     return week_map

# v2
# import re
# from datetime import datetime
# import json


# def format_working_hours(raw_hours_list):
#     """
#     Input: ['Wednesday: 08:00 - 02:00', 'Thursday: error string']
#     Output: JSON chuẩn, xử lý fallback nếu lỗi parse.
#     """
#     if not raw_hours_list:
#         return None

#     # Khởi tạo map kết quả
#     week_map = {
#         "monday": [], "tuesday": [], "wednesday": [], "thursday": [],
#         "friday": [], "saturday": [], "sunday": []
#     }

#     days_order = ["monday", "tuesday", "wednesday",
#                   "thursday", "friday", "saturday", "sunday"]

#     day_mapping = {
#         "monday": "monday", "mon": "monday",
#         "tuesday": "tuesday", "tue": "tuesday",
#         "wednesday": "wednesday", "wed": "wednesday",
#         "thursday": "thursday", "thu": "thursday",
#         "friday": "friday", "fri": "friday",
#         "saturday": "saturday", "sat": "saturday",
#         "sunday": "sunday", "sun": "sunday"
#     }

#     def parse_time(t_str):
#         t_str = t_str.strip()
#         formats = ["%I:%M %p", "%I %p", "%H:%M", "%I:%M%p"]
#         for fmt in formats:
#             try:
#                 return datetime.strptime(t_str.upper(), fmt).strftime("%H:%M")
#             except ValueError:
#                 continue
#         return "00:00"

#     for item in raw_hours_list:
#         if not item:
#             continue

#         clean_item = item.lower().replace('–', '-').replace('\u2009', ' ').strip()

#         # 1. Xác định thứ
#         found_day = None
#         for key, val in day_mapping.items():
#             if key in clean_item:
#                 found_day = val
#                 break

#         if not found_day:
#             continue

#         # 2. Parse giờ ban đầu
#         is_closed = "closed" in clean_item or "đóng cửa" in clean_item
#         start_time = "00:00"
#         end_time = "00:00"

#         if not is_closed:
#             if "24 hours" in clean_item or "cả ngày" in clean_item:
#                 start_time = "00:00"
#                 end_time = "23:59"
#             else:
#                 times = re.findall(
#                     r'(\d{1,2}:\d{2}\s?(?:am|pm)?)|(\d{1,2}\s?(?:am|pm))', clean_item)
#                 valid_times = [t[0] or t[1] for t in times if t[0] or t[1]]

#                 if len(valid_times) >= 2:
#                     start_time = parse_time(valid_times[0])
#                     end_time = parse_time(valid_times[1])

#         # === FIX 1: Xử lý Fallback dữ liệu lỗi ===
#         # Nếu không đóng cửa mà start=00:00 và end=00:00 -> Set mặc định 08:00 - 17:00
#         if not is_closed and start_time == "00:00" and end_time == "00:00":
#             start_time = "08:00"
#             # Mặc định 5 giờ chiều (17:00). Đổi thành "05:00" nếu muốn 5h sáng.
#             end_time = "17:00"

#         # 3. Logic thêm vào Map
#         if is_closed:
#             week_map[found_day].append({
#                 "day_of_week": found_day,
#                 "slot": len(week_map[found_day]) + 1,
#                 "start_time": "00:00",
#                 "end_time": "00:00",
#                 "is_closed": True
#             })

#         # Ca 24h hoặc ca từ 0h-23h59
#         elif start_time == "00:00" and end_time == "23:59":
#             week_map[found_day].append({
#                 "day_of_week": found_day,
#                 "slot": len(week_map[found_day]) + 1,
#                 "start_time": start_time,
#                 "end_time": end_time,
#                 "is_closed": False
#             })

#         # Logic tách ngày (Start > End)
#         elif start_time > end_time:
#             # === Slot 1: Ngày hiện tại ===
#             week_map[found_day].append({
#                 "day_of_week": found_day,
#                 "slot": len(week_map[found_day]) + 1,
#                 "start_time": start_time,
#                 "end_time": "23:59",
#                 "is_closed": False
#             })

#             # === FIX 2: Chỉ tạo Slot ngày hôm sau nếu End khác 00:00 ===
#             # Nếu end_time là "00:00" (tức nửa đêm), thì coi như hết ca ngày cũ, không tạo slot rỗng 00:00-00:00 ngày mới
#             if end_time != "00:00":
#                 current_idx = days_order.index(found_day)
#                 next_day_idx = (current_idx + 1) % 7
#                 next_day = days_order[next_day_idx]

#                 week_map[next_day].append({
#                     "day_of_week": next_day,
#                     "slot": len(week_map[next_day]) + 1,
#                     "start_time": "00:00",
#                     "end_time": end_time,
#                     "is_closed": False
#                 })

#         else:
#             # Giờ bình thường
#             week_map[found_day].append({
#                 "day_of_week": found_day,
#                 "slot": len(week_map[found_day]) + 1,
#                 "start_time": start_time,
#                 "end_time": end_time,
#                 "is_closed": False
#             })

#     return week_map


# ==========================================
# TEST CASE
# ==========================================
# raw_data = [
#     # Test FIX 2: Kết thúc đúng nửa đêm (Midnight)
#     'Friday: 11:00 PM – 02:00 PM',
#     'Saturday: error data'           # Test FIX 1: Dữ liệu lỗi -> Ra mặc định 08:00 - 17:00
# ]

# result = format_working_hours(raw_data)
# print(json.dumps(result, indent=4))

# v3
import re
from datetime import datetime
import json


def format_working_hours(raw_hours_list):
    """
    Input: ['Wednesday: 08:00 - 02:00', 'Thursday: error string']
    Output: JSON chuẩn, các slot trong ngày được sắp xếp tăng dần theo giờ bắt đầu.
    """
    if not raw_hours_list:
        return None

    # Khởi tạo map kết quả
    week_map = {
        "monday": [], "tuesday": [], "wednesday": [], "thursday": [],
        "friday": [], "saturday": [], "sunday": []
    }

    days_order = ["monday", "tuesday", "wednesday",
                  "thursday", "friday", "saturday", "sunday"]

    day_mapping = {
        "monday": "monday", "mon": "monday",
        "tuesday": "tuesday", "tue": "tuesday",
        "wednesday": "wednesday", "wed": "wednesday",
        "thursday": "thursday", "thu": "thursday",
        "friday": "friday", "fri": "friday",
        "saturday": "saturday", "sat": "saturday",
        "sunday": "sunday", "sun": "sunday"
    }

    def parse_time(t_str):
        t_str = t_str.strip()
        formats = ["%I:%M %p", "%I %p", "%H:%M", "%I:%M%p"]
        for fmt in formats:
            try:
                return datetime.strptime(t_str.upper(), fmt).strftime("%H:%M")
            except ValueError:
                continue
        return "00:00"

    # --- BƯỚC 1: PARSE DỮ LIỆU THÔ ---
    for item in raw_hours_list:
        if not item:
            continue

        clean_item = item.lower().replace('–', '-').replace('\u2009', ' ').strip()

        # 1. Xác định thứ
        found_day = None
        for key, val in day_mapping.items():
            if key in clean_item:
                found_day = val
                break

        if not found_day:
            continue

        # 2. Parse giờ ban đầu
        is_closed = "closed" in clean_item or "đóng cửa" in clean_item
        start_time = "00:00"
        end_time = "00:00"

        if not is_closed:
            if "24 hours" in clean_item or "cả ngày" in clean_item:
                start_time = "00:00"
                end_time = "23:59"
            else:
                times = re.findall(
                    r'(\d{1,2}:\d{2}\s?(?:am|pm)?)|(\d{1,2}\s?(?:am|pm))', clean_item)
                valid_times = [t[0] or t[1] for t in times if t[0] or t[1]]

                if len(valid_times) >= 2:
                    start_time = parse_time(valid_times[0])
                    end_time = parse_time(valid_times[1])

        # FIX 1: Xử lý Fallback dữ liệu lỗi
        if not is_closed and start_time == "00:00" and end_time == "00:00":
            start_time = "08:00"
            end_time = "17:00"

        # 3. Logic thêm vào Map (Chưa quan tâm thứ tự slot vội)
        # Lưu ý: Lúc này ta tạm thời gán slot=0, sẽ tính lại ở bước sau
        if is_closed:
            week_map[found_day].append({
                "day_of_week": found_day,
                "slot": 0,
                "start_time": "00:00",
                "end_time": "00:00",
                "is_closed": True
            })

        elif start_time == "00:00" and end_time == "23:59":
            week_map[found_day].append({
                "day_of_week": found_day,
                "slot": 0,
                "start_time": start_time,
                "end_time": end_time,
                "is_closed": False
            })

        elif start_time > end_time:
            # Slot ngày hiện tại
            week_map[found_day].append({
                "day_of_week": found_day,
                "slot": 0,
                "start_time": start_time,
                "end_time": "23:59",
                "is_closed": False
            })

            # FIX 2: Slot ngày hôm sau (chỉ khi end != 00:00)
            if end_time != "00:00":
                current_idx = days_order.index(found_day)
                next_day_idx = (current_idx + 1) % 7
                next_day = days_order[next_day_idx]

                week_map[next_day].append({
                    "day_of_week": next_day,
                    "slot": 0,
                    "start_time": "00:00",
                    "end_time": end_time,
                    "is_closed": False
                })

        else:
            week_map[found_day].append({
                "day_of_week": found_day,
                "slot": 0,
                "start_time": start_time,
                "end_time": end_time,
                "is_closed": False
            })

    # --- BƯỚC 2 (MỚI): HẬU XỬ LÝ - SẮP XẾP & ĐÁNH SỐ LẠI ---
    # Duyệt qua từng ngày trong tuần để sắp xếp lại các slot
    for day in days_order:
        slots = week_map[day]

        # Nếu ngày đó có dữ liệu (>= 1 slot)
        if slots:
            # 1. Sắp xếp list dựa trên start_time tăng dần
            # Chuỗi "00:00" luôn nhỏ hơn "17:00" nên sort string là đủ
            slots.sort(key=lambda x: x["start_time"])

            # 2. Cập nhật lại số thứ tự (slot index) sau khi sort
            for index, slot_data in enumerate(slots):
                slot_data["slot"] = index + 1

    return week_map


# ==========================================
# INPUT TEST DATA
# ==========================================

# test_scenarios = [
#     {
#         "name": "CASE 1: Cơ bản (Happy Path)",
#         "desc": "Giờ mở cửa hành chính bình thường, định dạng chuẩn.",
#         "input": [
#             "Monday: 08:00 - 17:00",
#             "Tuesday: 09:00 - 18:00",
#             "Wednesday: 08:30 - 17:30"
#         ]
#     },
#     {
#         "name": "CASE 2: Định dạng lộn xộn (Dirty Format)",
#         "desc": "Test khả năng Regex: AM/PM, không có số phút, khoảng trắng lạ, dấu gạch ngang khác nhau.",
#         "input": [
#             "Mon: 8am - 5pm",              # AM/PM không phút
#             "Tue: 8:30 am – 9:00 pm",      # Dấu gạch dài (–), có khoảng trắng
#             "Wed: 08:00-21:00",            # Dính liền
#             "Thu: 9 - 5 pm"                # Format dị (số 9 trống)
#         ]
#     },
#     {
#         "name": "CASE 3: 24h và Đóng cửa",
#         "desc": "Test logic Closed và 24 hours.",
#         "input": [
#             "Friday: Open 24 hours",
#             "Saturday: Cả ngày",
#             "Sunday: Closed",
#             "Monday: Đóng cửa"
#         ]
#     },
#     {
#         "name": "CASE 4: Xuyên đêm (Split Day)",
#         "desc": "Test logic cắt giờ khi Start > End (ví dụ quán Bar).",
#         "input": [
#             "Friday: 22:00 - 02:00",  # Phải sinh ra Fri 22-23:59 và Sat 00-02
#             "Saturday: 20:00 - 03:00"  # Phải sinh ra Sat 20-23:59 và Sun 00-03
#         ]
#     },
#     {
#         "name": "CASE 5: DEEP LOGIC - Xung đột thứ tự & Sắp xếp Slot",
#         "desc": "Đây là case quan trọng nhất để test đoạn code FIX vừa thêm. Thứ 3 vừa nhận ca thừa từ Thứ 2, vừa có ca riêng.",
#         "input": [
#             # Sẽ sinh ra slot rạng sáng Thứ 3 (00:00 - 04:00)
#             "Monday: 22:00 - 04:00",
#             "Tuesday: 10:00 - 18:00"  # Ca chính thức của Thứ 3
#         ]
#     },
#     {
#         "name": "CASE 6: DEEP LOGIC - Đảo ngược input",
#         "desc": "Input Thứ 3 nhập trước Thứ 2. Code phải tự sort lại slot cho đúng.",
#         "input": [
#             "Tuesday: 17:00 - 23:00",  # Nhập trước
#             "Monday: 22:00 - 02:00"   # Nhập sau, nhưng sẽ đẻ ra slot 00:00-02:00 vào sáng Thứ 3
#         ]
#         # Mong đợi ở Tuesday: Slot 1 (00:00-02:00), Slot 2 (17:00-23:00)
#     },
#     {
#         "name": "CASE 7: Fallback (Xử lý lỗi)",
#         "desc": "Input không chứa giờ hoặc định dạng không thể parse -> Về mặc định 08:00-17:00.",
#         "input": [
#             "Monday: Open today",    # Không có giờ -> Default
#             "Tuesday: Error string"  # Chuỗi lỗi -> Default
#         ]
#     },
#     {
#         "name": "CASE 8: Nửa đêm (Midnight Edge Case)",
#         "desc": "Test các mốc thời gian nhạy cảm 00:00.",
#         "input": [
#             "Wednesday: 00:00 - 23:59",  # Full ngày kiểu số
#             # Kết thúc đúng nửa đêm (Liệu có tạo slot ngày hôm sau không?)
#             "Thursday: 18:00 - 00:00"
#         ]
#     }
# ]

# # ==========================================
# # HÀM CHẠY TEST
# # ==========================================


# def run_tests():
#     for scenario in test_scenarios:
#         print("="*60)
#         print(f"RUNNING: {scenario['name']}")
#         print(f"Desc: {scenario['desc']}")
#         print(f"Input: {scenario['input']}")
#         print("-" * 20 + " KẾT QUẢ " + "-" * 20)

#         result = format_working_hours(scenario['input'])

#         # Chỉ in ra những ngày có dữ liệu để dễ nhìn
#         has_data = False
#         for day, slots in result.items():
#             if slots:
#                 has_data = True
#                 print(f"➤ {day.upper()}:")
#                 for s in slots:
#                     print(
#                         f"   - Slot {s['slot']}: {s['start_time']} -> {s['end_time']} (Closed: {s['is_closed']})")

#         if not has_data:
#             print("   (Không có dữ liệu đầu ra)")
#         print("\n")


# if __name__ == "__main__":
#     run_tests()
