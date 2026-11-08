import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time

st.set_page_config(page_title="🎹 鋼琴課程筆記系統", layout="wide")

# --- 0. 建立連線與讀取快取資料 ---
conn = st.connection("gsheets", type=GSheetsConnection)
sheet_url = "https://docs.google.com/spreadsheets/d/1Pl9tY9b2RIXXsEFfcgFGBzXr07fmoMLIUHz6Xczrzns/edit?gid=1002#gid=1002" # ⚠️ 請替換為真實 ID

df_books = conn.read(spreadsheet=sheet_url, worksheet="Books").dropna(how='all')
df_pieces = conn.read(spreadsheet=sheet_url, worksheet="Pieces").dropna(how='all')
df_lessons = conn.read(spreadsheet=sheet_url, worksheet="Lessons").dropna(how='all')
df_details = conn.read(spreadsheet=sheet_url, worksheet="Lesson_Details").dropna(how='all')

existing_books = df_books["book_title"].dropna().tolist() if not df_books.empty else []
if "(單曲/散譜)" not in existing_books:
    existing_books.insert(0, "(單曲/散譜)")

if 'keep_class_id' not in st.session_state:
    st.session_state.keep_class_id = int(df_lessons["class_id"].max()) + 1 if not df_lessons.empty and pd.notna(df_lessons["class_id"].max()) else 1

st.title("🎹 鋼琴課程筆記建檔系統")

tab1, tab2, tab3 = st.tabs(["📝 新增筆記", "📖 筆記總覽", "✏️ 編輯歷史筆記"])

# ==========================================
# 分頁 1：新增筆記 (Create)
# ==========================================
with tab1:
    st.header("1. 上課資訊")
    col1, col2 = st.columns(2)
    
    with col1:
        class_num = st.number_input("第幾堂課 (class_id)", min_value=1, step=1, value=st.session_state.keep_class_id)
    
    existing_lesson = df_lessons[df_lessons['class_id'] == class_num]
    
    if not existing_lesson.empty:
        # 【更新 3】明確提示修改 Metadata 的路徑
        st.info(f"ℹ️ 第 {class_num} 堂課已存在！系統已鎖定課程基本資訊，新曲目將直接附加至此堂課。\n\n"
                f"💡 **欲編輯日期或錄音檔等 Metadata，請至「✏️ 編輯歷史筆記」分頁，或是直接使用 Google Sheet 編輯。**")
        
        class_date_str = existing_lesson['date'].values[0]
        audio_file_str = str(existing_lesson['audio_filename'].values[0]) if pd.notna(existing_lesson['audio_filename'].values[0]) else ""
        
        with col2:
            st.text_input("上課日期 (已鎖定)", value=class_date_str, disabled=True)
        audio_file = st.text_input("錄音檔名稱 (已鎖定)", value=audio_file_str, disabled=True)
        class_date = class_date_str 
    else:
        with col2:
            class_date = st.date_input("上課日期")
        audio_file = st.text_input("錄音檔名稱", placeholder="例如: class69_chopin.m4a")
        
    st.divider()

    st.header("2. 練習明細與重點")
    book_choice = st.selectbox("選擇書本來源", ["-- 選擇既有書本 --"] + existing_books + ["➕ 新增其他書本..."])

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
        if book_choice == "(單曲/散譜)":
            current_book_id = 0 
        else:
            current_book_id = df_books.loc[df_books["book_title"] == book_choice, "book_id"].values[0]

    st.markdown("##### 🎵 練習曲目內容")
    existing_pieces_in_book = []
    if current_book_id is not None:
        existing_pieces_in_book = df_pieces[df_pieces["book_id"] == current_book_id]["piece_name"].dropna().tolist()

    piece_choice = st.selectbox("選擇或新增曲目", ["-- 選擇曲目 --"] + existing_pieces_in_book + ["➕ 新增曲目..."])

    piece_name = None
    if piece_choice == "➕ 新增曲目...":
        piece_name = st.text_input("輸入新曲目名稱 / 標號", placeholder="例如: No. 20 in C-sharp minor")
    elif piece_choice != "-- 選擇曲目 --":
        piece_name = piece_choice

    col5, col6 = st.columns(2)
    with col5:
        page_num = st.text_input("頁數", placeholder="例如: p.32")
    with col6:
        measures = st.text_input("練習小節", placeholder="例如: 1-15")
        
    focus = st.text_area("練習重點")

    st.markdown("---")
    keep_same_class = st.checkbox("🔄 儲存後留在同一堂課 (適合一堂課要記錄多首曲目時勾選)", value=False)

    if st.button("💾 儲存新筆記", type="primary"):
        try:
            if book_choice == "-- 選擇既有書本 --" or piece_choice == "-- 選擇曲目 --":
                st.error("請確認已選擇書本與曲目！")
                st.stop()
                
            # 1. 寫入 Books
            if book_choice == "➕ 新增其他書本...":
                if not new_book_title:
                    st.error("請填寫新書本的「中文書名」！")
                    st.stop()
                current_book_id = int(df_books["book_id"].max()) + 1 if not df_books.empty and pd.notna(df_books["book_id"].max()) else 1
                new_book_record = pd.DataFrame([{"book_id": current_book_id, "book_title": new_book_title, "original_title": new_original_title, "author_editor": new_author, "publisher": new_publisher, "series": new_series, "publish_date": new_publish_date, "description": new_description, "isbn": new_isbn}])
                df_books = pd.concat([df_books, new_book_record], ignore_index=True)
                conn.update(spreadsheet=sheet_url, worksheet="Books", data=df_books)

            # 2. 寫入 Pieces
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

            # 【更新 1：防止重複新增同一首曲子】
            duplicate_check = df_details[(df_details["class_id"] == class_num) & (df_details["piece_id"] == current_piece_id)]
            if not duplicate_check.empty:
                st.error(f"⚠️ 第 {class_num} 堂課已經有這首曲子的紀錄了！請前往「✏️ 編輯歷史筆記」分頁進行修改。")
                st.stop()

            # 3. 寫入 Lessons
            if existing_lesson.empty:
                new_lesson_record = pd.DataFrame([{"class_id": class_num, "date": str(class_date), "audio_filename": audio_file}])
                df_lessons = pd.concat([df_lessons, new_lesson_record], ignore_index=True)
                conn.update(spreadsheet=sheet_url, worksheet="Lessons", data=df_lessons)

            # 4. 寫入 Lesson_Details
            new_detail_id = int(df_details["detail_id"].max()) + 1 if not df_details.empty and pd.notna(df_details["detail_id"].max()) else 1
            new_detail_record = pd.DataFrame([{"detail_id": new_detail_id, "class_id": class_num, "piece_id": current_piece_id, "page": page_num, "measures": measures, "focus": focus}])
            df_details = pd.concat([df_details, new_detail_record], ignore_index=True)
            conn.update(spreadsheet=sheet_url, worksheet="Lesson_Details", data=df_details)
            
            if keep_same_class:
                st.session_state.keep_class_id = class_num
            else:
                st.session_state.keep_class_id = class_num + 1

            st.success(f"第 {class_num} 堂課筆記已成功寫入資料庫！")
            st.balloons()
            st.cache_data.clear() 
            time.sleep(1.5)
            st.rerun()
            
        except Exception as e:
            st.error(f"寫入失敗：{e}")


# ==========================================
# 分頁 2：筆記總覽 (Read / View)
# ==========================================
with tab2:
    st.header("歷史筆記總覽")
    if df_details.empty:
        st.info("目前尚無筆記。")
    else:
        df_view = df_details.merge(df_lessons, on="class_id", how="left") \
                            .merge(df_pieces, on="piece_id", how="left") \
                            .merge(df_books, on="book_id", how="left")
        df_view = df_view.sort_values(by=["class_id", "detail_id"], ascending=[False, False])
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            all_books_in_records = df_view["book_title"].dropna().unique().tolist()
            filter_book = st.selectbox("📖 過濾書本", ["顯示全部"] + all_books_in_records)
        with col_f2:
            if filter_book != "顯示全部":
                pieces_in_filtered_book = df_view[df_view["book_title"] == filter_book]["piece_name"].dropna().unique().tolist()
                filter_piece = st.selectbox("🎵 過濾曲目", ["顯示全部"] + pieces_in_filtered_book)
            else:
                filter_piece = st.selectbox("🎵 過濾曲目", ["顯示全部"], disabled=True)
                
        df_display = df_view.copy()
        if filter_book != "顯示全部":
            df_display = df_display[df_display["book_title"] == filter_book]
            if filter_piece != "顯示全部":
                df_display = df_display[df_display["piece_name"] == filter_piece]

        display_cols = {
            'class_id': '堂數',
            'date': '上課日期',
            'book_title': '書本來源',
            'piece_name': '曲目',
            'page': '頁數',
            'measures': '小節',
            'focus': '練習重點',
            'audio_filename': '錄音檔'
        }
        df_display = df_display[list(display_cols.keys())].rename(columns=display_cols)
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# ==========================================
# 分頁 3：編輯歷史筆記 (Update)
# ==========================================
with tab3:
    st.header("修改已存在的筆記")
    if df_details.empty:
        st.info("目前還沒有任何筆記紀錄喔！")
    else:
        def safe_str(val):
            if pd.isna(val): return ""
            if isinstance(val, float) and val.is_integer(): return str(int(val))
            return str(val)

        available_classes = sorted(df_details['class_id'].dropna().unique().tolist(), reverse=True)
        selected_class = st.selectbox("選擇要修改的課堂", available_classes, format_func=lambda x: f"第 {int(x)} 堂課")
        
        if selected_class:
            st.divider()
            
            # 【更新 2：新增修改課程 Metadata 的區塊】
            st.subheader("🗓️ 編輯課程基本資訊 (Metadata)")
            class_meta = df_lessons[df_lessons['class_id'] == selected_class]
            
            if not class_meta.empty:
                old_date = class_meta['date'].values[0]
                old_audio = class_meta['audio_filename'].values[0]
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    edit_date = st.text_input("修改上課日期 (格式: YYYY-MM-DD)", value=safe_str(old_date))
                with col_m2:
                    edit_audio = st.text_input("修改錄音檔名稱", value=safe_str(old_audio))
                    
                if st.button("💾 更新課程資訊", key="btn_update_meta"):
                    try:
                        idx_lesson = df_lessons[df_lessons['class_id'] == selected_class].index[0]
                        df_lessons.loc[idx_lesson, 'date'] = edit_date
                        df_lessons.loc[idx_lesson, 'audio_filename'] = edit_audio
                        
                        conn.update(spreadsheet=sheet_url, worksheet="Lessons", data=df_lessons)
                        st.success("課程基本資訊更新成功！")
                        st.cache_data.clear()
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新課程資訊失敗：{e}")
            
            st.divider()
            
            # 編輯該堂課曲目明細
            st.subheader("🎵 編輯曲目筆記明細")
            class_details = df_details[df_details['class_id'] == selected_class]
            display_options = []
            detail_mapping = {} 
            
            for idx, row in class_details.iterrows():
                d_id = row['detail_id']
                p_id = row['piece_id']
                
                p_row = df_pieces[df_pieces['piece_id'] == p_id]
                p_name = p_row['piece_name'].values[0] if not p_row.empty else "未知曲目"
                
                display_str = f"{p_name}"
                display_options.append(display_str)
                detail_mapping[display_str] = d_id
                
            selected_piece_str = st.selectbox("選擇該堂課的曲目進行編輯", display_options)
            
            if selected_piece_str:
                target_detail_id = detail_mapping[selected_piece_str]
                current_record = class_details[class_details['detail_id'] == target_detail_id].iloc[0]
                
                st.markdown("##### ✏️ 編輯內容")
                col7, col8 = st.columns(2)
                with col7:
                    edit_page = st.text_input("修改頁數", value=safe_str(current_record.get('page', '')))
                with col8:
                    edit_measures = st.text_input("修改小節", value=safe_str(current_record.get('measures', '')))
                    
                edit_focus = st.text_area("修改重點", value=safe_str(current_record.get('focus', '')), height=150)
                
                if st.button("💾 更新此筆記", type="primary", key="btn_update_detail"):
                    try:
                        idx = df_details[df_details['detail_id'] == target_detail_id].index[0]
                        df_details.loc[idx, 'page'] = edit_page
                        df_details.loc[idx, 'measures'] = edit_measures
                        df_details.loc[idx, 'focus'] = edit_focus
                        conn.update(spreadsheet=sheet_url, worksheet="Lesson_Details", data=df_details)
                        
                        st.success("舊筆記明細更新成功！")
                        st.cache_data.clear()
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新筆記失敗：{e}")