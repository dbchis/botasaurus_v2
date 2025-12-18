import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from crawler import run_crawler_logic

# --- CẤU HÌNH ---
DATA_FILE = 'locations.json'
HISTORY_FILE = 'history.json'
OUTPUT_DIR = os.path.join("output", "data")  # Thư mục chứa file kết quả

# --- HÀM HỖ TRỢ ---


def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {"types": ["Nhà hàng"], "locations": {
            "Hà Nội": {"Hai Bà Trưng": ["Bạch Mai"]}}}
        save_data(default_data)
        return default_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_history(entry):
    history = load_history()
    history.insert(0, entry)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# Hàm đọc nội dung file JSON kết quả


def read_result_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="AI-DCAS", page_icon="🦖", layout="wide")
st.title("🦖 AI-DCAS")

db = load_data()
types_list = db.get('types', [])
locations_db = db.get('locations', {})

# THÊM TAB 4: KHO DỮ LIỆU
tab1, tab2, tab3, tab4 = st.tabs(
    ["🚀 Chạy Tool", "⚙️ Quản lý Dữ liệu", "📜 Lịch sử", "📂 Kho Dữ liệu (Output)"])

# === TAB 1: CHẠY TOOL ===
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cấu hình chạy")
        selected_type = st.selectbox("Chọn loại hình", types_list)
        cities = list(locations_db.keys())
        selected_city = st.selectbox("Tỉnh / Thành phố", cities)

        districts = []
        if selected_city:
            districts = list(locations_db[selected_city].keys())
        selected_district = st.selectbox("Quận / Huyện", districts)

        wards = []
        if selected_city and selected_district:
            wards = locations_db[selected_city][selected_district]
        selected_wards = st.multiselect("Phường / Xã (Chọn nhiều)", wards)

        num_result = st.number_input(
            "Số lượng (numResult)", min_value=1, value=50)
        street_opt = st.text_input("Đường phố (Optional)")

    with col2:
        st.subheader("Trạng thái")
        if st.button("BẮT ĐẦU QUÉT 🚀", type="primary"):
            if not selected_wards:
                st.error("Vui lòng chọn ít nhất một Phường/Xã!")
            else:
                inputs = []
                for ward in selected_wards:
                    inputs.append({
                        "type": selected_type,
                        "street": street_opt,
                        "ward": ward,
                        "county": selected_district,
                        "city": selected_city,
                        "province": "",
                        "numResult": num_result
                    })

                # Biến lưu kết quả để hiển thị ngay sau khi chạy
                latest_results = []

                with st.status("Đang thực thi...", expanded=True) as status:
                    # Gọi hàm wrapper
                    logs, file_paths = run_crawler_logic(inputs)

                    for log in logs:
                        if "✅" in log:
                            st.success(log)
                        elif "❌" in log:
                            st.error(log)
                        elif "⚠️" in log:
                            st.warning(log)
                        else:
                            st.write(log)

                    status.update(label="Hoàn tất!",
                                  state="complete", expanded=False)

                    # Load data vừa chạy để hiển thị
                    for fp in file_paths:
                        data = read_result_file(fp)
                        if data:
                            latest_results.append(
                                {"file": os.path.basename(fp), "content": data})

                # Lưu lịch sử
                save_history({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": selected_type,
                    "location": f"{selected_district}, {selected_city}",
                    "wards_count": len(selected_wards),
                    "files": file_paths
                })

                # --- HIỂN THỊ KẾT QUẢ NGAY LẬP TỨC ---
                st.divider()
                st.subheader("📊 Kết quả vừa thu thập:")
                for res in latest_results:
                    with st.expander(f"Xem dữ liệu: {res['file']}", expanded=True):
                        content = res['content']
                        # Xử lý format mới {query, total, data: []}
                        if isinstance(content, dict) and 'data' in content:
                            st.write(
                                f"🔎 Query: **{content.get('query')}** | Total: **{content.get('total_found')}**")
                            df = pd.DataFrame(content['data'])
                            st.dataframe(df, use_container_width=True)
                        elif isinstance(content, list):
                            st.dataframe(pd.DataFrame(content),
                                         use_container_width=True)
                        else:
                            st.json(content)

# === TAB 2: QUẢN LÝ DỮ LIỆU ===
with tab2:
    st.header("Thêm dữ liệu địa điểm mới")
    c1, c2 = st.columns(2)
    with c1:
        new_type = st.text_input("Nhập loại hình mới")
        if st.button("Thêm Type"):
            if new_type and new_type not in db['types']:
                db['types'].append(new_type)
                save_data(db)
                st.rerun()
    with c2:
        add_city = st.text_input("Thêm Thành phố", key="add_city")
        add_district = st.text_input("Thêm Quận/Huyện", key="add_dist")
        add_ward = st.text_input("Thêm Phường/Xã", key="add_ward")
        if st.button("Lưu Địa Điểm"):
            if add_city and add_district and add_ward:
                if add_city not in db['locations']:
                    db['locations'][add_city] = {}
                if add_district not in db['locations'][add_city]:
                    db['locations'][add_city][add_district] = []
                if add_ward not in db['locations'][add_city][add_district]:
                    db['locations'][add_city][add_district].append(add_ward)
                    save_data(db)
                    st.success("Đã thêm!")
                    st.rerun()

# === TAB 3: LỊCH SỬ ===
with tab3:
    st.header("Lịch sử chạy Tool")
    history_data = load_history()
    if history_data:
        st.dataframe(pd.DataFrame(history_data), use_container_width=True)
    else:
        st.info("Chưa có lịch sử.")

# === TAB 4: KHO DỮ LIỆU (FILE VIEWER) ===
with tab4:
    st.header("📂 Danh sách file Output")

    # 1. Quét file trong thư mục output
    if not os.path.exists(OUTPUT_DIR):
        st.warning(
            f"Chưa có thư mục {OUTPUT_DIR}. Hãy chạy tool ít nhất 1 lần.")
    else:
        # Lấy danh sách file JSON và sắp xếp theo thời gian mới nhất
        files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]
        # Sort ngược (Z-A) vì tên file bắt đầu bằng timestamp, nên file mới nhất sẽ ở đầu
        files.sort(reverse=True)

        if not files:
            st.info("Thư mục trống.")
        else:
            col_list, col_view = st.columns([1, 3])

            with col_list:
                st.write(f"Tìm thấy **{len(files)}** file.")
                selected_file = st.selectbox(
                    "Chọn file để xem:", files, index=0)

                # Hiển thị thông tin file
                file_full_path = os.path.join(OUTPUT_DIR, selected_file)
                file_stat = os.stat(file_full_path)
                file_size_kb = file_stat.st_size / 1024
                file_time = datetime.fromtimestamp(
                    file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                st.info(
                    f"📅 **Ngày tạo:** {file_time}\n\n"
                    f"💾 **Kích thước:** {file_size_kb:.2f} KB"
                )

            with col_view:
                st.subheader(f"Nội dung file: {selected_file}")

                try:
                    data = read_result_file(file_full_path)

                    # Chuyển đổi view (Table vs Raw JSON)
                    view_mode = st.radio(
                        "Chế độ xem:", ["Bảng (Table)", "JSON thô"], horizontal=True)

                    if view_mode == "Bảng (Table)":
                        # Xử lý logic hiển thị tùy theo cấu trúc JSON
                        # Case 1: Cấu trúc mới {query, total, data: [...]}
                        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                            st.caption(
                                f"Query: {data.get('query')} | Total Found: {data.get('total_found')}")
                            df = pd.DataFrame(data['data'])
                            st.dataframe(df, use_container_width=True)

                        # Case 2: Cấu trúc cũ (List of objects)
                        elif isinstance(data, list):
                            df = pd.DataFrame(data)
                            st.dataframe(df, use_container_width=True)

                        # Case 3: Khác
                        else:
                            st.warning(
                                "Cấu trúc file không hỗ trợ hiển thị dạng bảng. Vui lòng xem dạng JSON thô.")
                            st.json(data)

                    else:
                        # View Raw JSON
                        st.json(data)

                except Exception as e:
                    st.error(f"Không thể đọc file: {e}")
