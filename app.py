import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="🎹 鋼琴課程筆記系統", layout="centered")

# --- 0. 建立連線與讀取快取資料 ---
conn = st.connection("gsheets", type=GSheetsConnection)
sheet_url = "https://docs.google.com/spreadsheets/d/1Pl9tY9b2RIXXsEFfcgFGBzXr07fmoMLIUHz6Xczrzns/edit?gid=0#gid=0" # 請確保這裡是正確的 ID

# 讀取 Books 工作表
df_books = conn.read(spreadsheet=sheet_url, worksheet="Books")
# 從 df_books 提取現有的書名，並確保沒有空值
existing_books = df_books["book_title"].dropna().tolist() if not df_books.empty else []

st.title("🎹 鋼琴課程筆記建檔系統")

# --- 1. 上課基本資訊 ---
st.header("1. 上課資訊")
col1, col2 = st.columns(2)
with col1:
    class_num = st.number_input("第幾堂課 (class_id)", min_value=1, step=1)
with col2:
    class_date = st.date_input("上課日期")
audio_file = st.text_input("錄音檔名稱", placeholder="例如: class69_chopin.m4a")
st.divider()

# --- 2. 書本與曲目選擇 ---
st.header("2. 練習明細與重點")

book_choice = st.selectbox("選擇書本", ["-- 選擇既有書本 --"] + existing_books + ["➕ 新增其他書本..."])

# 如果選擇新增書本，則顯示額外的 Metadata 輸入框
if book_choice == "➕ 新增其他書本...":
    st.markdown("##### 📖 新增書本詳細資訊 (Metadata)")
    new_book_title = st.text_input("中文書名", placeholder="例如: 蕭邦【原典版】夜曲")
    new_original_title = st.text_input("原文書名", placeholder="例如: Chopin Nocturnes")
    
    col3, col4 = st.columns(2)
    with col3:
        new_author = st.text_input("作者 / 編訂者")
        new_publisher = st.text_input("出版社")
    with col4:
        new_series = st.text_input("系列名稱")
        new_publish_date = st.text_input("出版日期")
        
    new_description = st.text_area("書籍解說 / 簡介 (供 RAG 語意關聯使用)")
    new_isbn = st.text_input("ISBN (選填)")
    
    st.divider() # 視覺分隔線：將書本資訊與下方曲目資訊隔開

# 無論是選擇既有書本還是新增書本，都會顯示曲目與練習重點的輸入框
st.markdown("##### 🎵 練習曲目內容")
piece_name = st.text_input("曲目名稱 / 標號", placeholder="例如: No. 20 in C-sharp minor")
measures = st.text_input("練習小節", placeholder="例如: 1-15")
focus = st.text_area("練習重點")

# --- 3. 儲存按鈕與寫入邏輯 ---
if st.button("💾 儲存筆記", type="primary"):
    # 這裡未來會放入寫入 Google Sheets 的程式碼
    # 包含：
    # 1. 如果是新書本，先 Append 到 Books 表，並取得新的 book_id
    # 2. 如果是新曲目，Append 到 Pieces 表，取得 piece_id
    # 3. 將上課資訊 Append 到 Lessons 表
    # 4. 將練習細節 Append 到 Lesson_Details 表
    st.success(f"第 {class_num} 堂課筆記測試送出成功！")
    st.balloons()