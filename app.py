import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time

st.set_page_config(page_title="🎹 鋼琴課程筆記系統", layout="centered")

# --- 0. 建立連線與讀取快取資料 ---
conn = st.connection("gsheets", type=GSheetsConnection)
sheet_url = "https://docs.google.com/spreadsheets/d/1Pl9tY9b2RIXXsEFfcgFGBzXr07fmoMLIUHz6Xczrzns/edit?gid=1003#gid=1003" # 請替換為真實 ID

# 讀取現有資料
df_books = conn.read(spreadsheet=sheet_url, worksheet="Books")
df_pieces = conn.read(spreadsheet=sheet_url, worksheet="Pieces")
df_lessons = conn.read(spreadsheet=sheet_url, worksheet="Lessons")
df_details = conn.read(spreadsheet=sheet_url, worksheet="Lesson_Details")

# 準備下拉選單資料
existing_books = df_books["book_title"].dropna().tolist() if not df_books.empty else []
# 確保 (單曲/散譜) 選項存在
if "(單曲/散譜)" not in existing_books:
    existing_books.insert(0, "(單曲/散譜)")

st.title("🎹 鋼琴課程筆記建檔系統")

# --- 1. 上課基本資訊 (Lessons) ---
st.header("1. 上課資訊")
col1, col2 = st.columns(2)
with col1:
    # 自動帶出下一堂課的號碼
    next_class_id = int(df_lessons["class_id"].max()) + 1 if not df_lessons.empty and pd.notna(df_lessons["class_id"].max()) else 1
    class_num = st.number_input("第幾堂課 (class_id)", min_value=1, step=1, value=next_class_id)
with col2:
    class_date = st.date_input("上課日期")
audio_file = st.text_input("錄音檔名稱", placeholder="例如: class69_chopin.m4a")
st.divider()

# --- 2. 書本與曲目選擇 (Books & Pieces) ---
st.header("2. 練習明細與重點")

book_choice = st.selectbox("選擇書本來源", ["-- 選擇既有書本 --"] + existing_books + ["➕ 新增其他書本..."])

# 處理書本選擇
current_book_id = None
if book_choice == "➕ 新增其他書本...":
    st.markdown("##### 📖 新增書本詳細資訊")
    new_book_title = st.text_input("中文書名", placeholder="例如: 蕭邦【原典版】夜曲")
    new_original_title = st.text_input("原文書名", placeholder="例如: Chopin Nocturnes")
    col3, col4 = st.columns(2)
    with col3:
        new_author = st.text_input("作者 / 編訂者")
        new_publisher = st.text_input("出版社")
    with col4:
        new_series = st.text_input("系列名稱")
        new_publish_date = st.text_input("出版日期")
    new_description = st.text_area("書籍解說 / 簡介")
    new_isbn = st.text_input("ISBN (選填)")
    st.divider()
elif book_choice != "-- 選擇既有書本 --":
    # 取得選擇書本的 ID
    if book_choice == "(單曲/散譜)":
        current_book_id = 0 # 約定 0 代表單曲/散譜
    else:
        current_book_id = df_books.loc[df_books["book_title"] == book_choice, "book_id"].values[0]

# 處理曲目選擇 (連動下拉選單)
st.markdown("##### 🎵 練習曲目內容")
existing_pieces_in_book = []
if current_book_id is not None:
    # 過濾出該本書底下的既有曲目
    existing_pieces_in_book = df_pieces[df_pieces["book_id"] == current_book_id]["piece_name"].dropna().tolist()

piece_choice = st.selectbox("選擇或新增曲目", ["-- 選擇曲目 --"] + existing_pieces_in_book + ["➕ 新增曲目..."])

piece_name = None
if piece_choice == "➕ 新增曲目...":
    piece_name = st.text_input("輸入新曲目名稱 / 標號", placeholder="例如: No. 20 in C-sharp minor")
elif piece_choice != "-- 選擇曲目 --":
    piece_name = piece_choice

# 頁數與小節
col5, col6 = st.columns(2)
with col5:
    page_num = st.text_input("頁數", placeholder="例如: p.32")
with col6:
    measures = st.text_input("練習小節", placeholder="例如: 1-15")
    
focus = st.text_area("練習重點")

# --- 3. 儲存按鈕與完整寫入邏輯 ---
if st.button("💾 儲存筆記", type="primary"):
    try:
        # 防呆檢查
        if book_choice == "-- 選擇既有書本 --" or piece_choice == "-- 選擇曲目 --":
            st.error("請確認已選擇書本與曲目！")
            st.stop()
            
        # 1. 寫入 Books 表 (如果是新書)
        if book_choice == "➕ 新增其他書本...":
            if not new_book_title:
                st.error("請填寫新書本的「中文書名」！")
                st.stop()
            current_book_id = int(df_books["book_id"].max()) + 1 if not df_books.empty and pd.notna(df_books["book_id"].max()) else 1
            new_book_record = pd.DataFrame([{"book_id": current_book_id, "book_title": new_book_title, "original_title": new_original_title, "author_editor": new_author, "publisher": new_publisher, "series": new_series, "publish_date": new_publish_date, "description": new_description, "isbn": new_isbn}])
            df_books = pd.concat([df_books, new_book_record], ignore_index=True)
            conn.update(spreadsheet=sheet_url, worksheet="Books", data=df_books)

        # 2. 寫入 Pieces 表 (如果是新曲目)
        current_piece_id = None
        if piece_choice == "➕ 新增曲目...":
            if not piece_name:
                st.error("請填寫「新曲目名稱」！")
                st.stop()
            current_piece_id = int(df_pieces["piece_id"].max()) + 1 if not df_pieces.empty and pd.notna(df_pieces["piece_id"].max()) else 1
            new_piece_record = pd.DataFrame([{"piece_id": current_piece_id, "book_id": current_book_id, "piece_name": piece_name}])
            df_pieces = pd.concat([df_pieces, new_piece_record], ignore_index=True)
            conn.update(spreadsheet=sheet_url, worksheet="Pieces", data=df_pieces)
        else:
            current_piece_id = df_pieces[(df_pieces["book_id"] == current_book_id) & (df_pieces["piece_name"] == piece_choice)]["piece_id"].values[0]

        # 3. 寫入 Lessons 表 (檢查該堂課是否已存在，避免同一堂課錄多首歌時重複寫入)
        if class_num not in df_lessons["class_id"].values:
            new_lesson_record = pd.DataFrame([{"class_id": class_num, "date": str(class_date), "audio_filename": audio_file}])
            df_lessons = pd.concat([df_lessons, new_lesson_record], ignore_index=True)
            conn.update(spreadsheet=sheet_url, worksheet="Lessons", data=df_lessons)

        # 4. 寫入 Lesson_Details 表
        new_detail_id = int(df_details["detail_id"].max()) + 1 if not df_details.empty and pd.notna(df_details["detail_id"].max()) else 1
        new_detail_record = pd.DataFrame([{"detail_id": new_detail_id, "class_id": class_num, "piece_id": current_piece_id, "page": page_num, "measures": measures, "focus": focus}])
        df_details = pd.concat([df_details, new_detail_record], ignore_index=True)
        conn.update(spreadsheet=sheet_url, worksheet="Lesson_Details", data=df_details)
        
        st.success(f"第 {class_num} 堂課筆記已成功寫入資料庫！")
        st.balloons()
        
        st.cache_data.clear() 
        time.sleep(2)
        st.rerun()
        
    except Exception as e:
        st.error(f"寫入失敗：{e}")