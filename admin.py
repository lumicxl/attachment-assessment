import streamlit as st
import pandas as pd
from db import init_db, list_subjects, list_sessions, export_csv

st.set_page_config(page_title="后台管理", layout="wide")
st.title("ASAARA 后台管理")

init_db()

tab1, tab2, tab3 = st.tabs(["被试列表", "测评记录", "导出数据"])

with tab1:
    st.subheader("被试列表")
    subjects = list_subjects()
    if subjects:
        st.dataframe(pd.DataFrame(subjects))
    else:
        st.info("暂无被试")

with tab2:
    st.subheader("测评记录")
    sessions = list_sessions()
    if sessions:
        st.dataframe(pd.DataFrame(sessions))
    else:
        st.info("暂无测评记录")

with tab3:
    st.subheader("导出 CSV")
    if st.button("导出 data/export.csv"):
        path = export_csv()
        st.success(f"已导出：{path}")
        with open(path, "rb") as f:
            st.download_button("下载 CSV", f.read(), file_name="asaara_export.csv", mime="text/csv")