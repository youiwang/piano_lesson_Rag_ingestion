import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="🎹 鋼琴課程筆記系統")

# 1. 建立連線並讀取資料
conn = st.connection("gsheets", type=GSheetsConnection)

# 替換成你的 Google Sheets 網址
sheet_url = "https://docs.google.com/spreadsheets/d/你的_SHEET_ID/edit"

# 讀取 Books 工作表 (做為快取)
df_books = conn.read(spreadsheet=sheet_url, worksheet="Books")
existing_books = df_books["book_title"].dropna().tolist() if not df_books.empty else []

st.title("🎹 鋼琴課程筆記建檔系統")

# 2. 上課基本資訊輸入
col1, col2 = st.columns(2)
with col1:
    class_num = st.number_input("第幾堂課 (class_id)", min_value=1, step=1)
with col2:
    class_date = st.date_input("上課日期")
    
audio_file = st.text_input("錄音檔名稱 (例如: class69_chopin.m4a)")

st.divider()

# 3. 書本與曲目選擇
st.subheader("練習明細與重點")
book_choice = st.selectbox("選擇書本", ["-- 選擇既有書本 --"] + existing_books + ["➕ 新增其他書本..."])

if book_choice == "➕ 新增其他書本...":
    new_book = st.text_input("輸入新書本名稱")
    # 實際專案中，這裡可以再寫一段邏輯先更新 df_books
    
piece_name = st.text_input("曲目名稱 / 標號 (例如: No. 20 in C-sharp minor)")
measures = st.text_input("練習小節 (例如: 1-15)")
focus = st.text_area("練習重點")

# 4. 寫回 Google Sheets
if st.button("💾 儲存筆記"):
    # 讀取目前的 Lesson_Details
    df_details = conn.read(spreadsheet=sheet_url, worksheet="Lesson_Details")
    
    # 建立新一筆資料
    new_record = pd.DataFrame([{
        "detail_id": len(df_details) + 1,
        "class_id": class_num,
        "piece_id": 99, # 簡化示範，實務上需對應 Pieces 表的 ID
        "measures": measures,
        "focus": focus
    }])
    
    # 合併並更新寫回 Google Sheets
    updated_details = pd.concat([df_details, new_record], ignore_index=True)
    conn.update(worksheet="Lesson_Details", data=updated_details)
    
    st.success(f"第 {class_num} 堂課筆記已成功寫入資料庫！")
    st.balloons()