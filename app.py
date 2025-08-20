# app.py
import io
import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_numeric_dtype, is_object_dtype, is_string_dtype
)

st.set_page_config(page_title="CSV/Excel Cleaner", page_icon="🧽", layout="wide")
st.title("🧽 CSV/Excel Cleaner 🧹✨")

st.write("Upload CSV/XLSX/XLS, choose cleaning mode, preview, and download.")

uploaded_file = st.file_uploader("Choose a CSV, XLSX, or XLS file", type=["csv","xlsx","xls"])

def read_any_table(file) -> pd.DataFrame:
    name = file.name.lower()
    if name.endswith(".csv"):
        try:
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0); return pd.read_csv(file, encoding="latin-1")
    file.seek(0)
    try:
        xls = pd.ExcelFile(file, engine="openpyxl")      # .xlsx
        sheet = st.selectbox("Select sheet", xls.sheet_names, index=0)
        return pd.read_excel(xls, sheet_name=sheet)
    except Exception:
        file.seek(0)
        xls = pd.ExcelFile(file, engine="xlrd")          # .xls
        sheet = st.selectbox("Select sheet", xls.sheet_names, index=0)
        return pd.read_excel(xls, sheet_name=sheet)

st.markdown("### 🔧 Choose Cleaning Mode")
mode = st.radio(
    "Select one:",
    [
        "🧹 Basic Cleaning – Remove blank rows and repeated rows",
        "✨ Smart Cleaning (Mean Fill) – Remove blank & repeated rows, fill in missing data",
        "🔢 Smart Cleaning (Zero Fill) – Remove blank & repeated rows, numbers with 0"
    ],
    index=0
)

if uploaded_file:
    df = read_any_table(uploaded_file)
    st.subheader("📊 Original data (first 50 rows)")
    st.dataframe(df.head(50), use_container_width=True)

    # 1️⃣ Drop rows that are completely empty
    df_cleaned = df.dropna(how="all")

    # 2️⃣ Smart cleaning
    if "Smart" in mode:
        for col in df_cleaned.columns:
            # Treat blank/whitespace strings as missing
            s = df_cleaned[col].replace(r'^\s*$', pd.NA, regex=True)

            if is_numeric_dtype(s):
                if "Mean" in mode:
                    mean_val = pd.to_numeric(s, errors="coerce").mean()
                    if pd.isna(mean_val):
                        mean_val = 0
                    df_cleaned[col] = s.fillna(mean_val)
                elif "Zero" in mode:
                    df_cleaned[col] = s.fillna(0)

            elif is_string_dtype(s) or is_object_dtype(s):
                df_cleaned[col] = s.fillna("N/A")

            else:
                df_cleaned[col] = s

    # 3️⃣ Drop duplicates
    df_cleaned = df_cleaned.drop_duplicates()

    # ℹ️ Metrics
    before_rows = len(df); after_rows = len(df_cleaned)
    removed_rows = before_rows - after_rows
    before_na = int(df.isna().replace(r'^\s*$', pd.NA, regex=True).sum().sum())
    after_na = int(df_cleaned.isna().sum().sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows removed", removed_rows)
    c2.metric("Cells filled", max(0, before_na - after_na))
    c3.metric("Final rows", after_rows)

    # ✅ Show cleaned data
    st.subheader("📊 Cleaned data (first 50 rows)")
    st.dataframe(df_cleaned.head(50), use_container_width=True)

    # 💾 Downloads
    csv_bytes = df_cleaned.to_csv(index=False).encode("utf-8")
    st.download_button("💾 Download cleaned CSV", data=csv_bytes,
                       file_name="cleaned.csv", mime="text/csv",
                       use_container_width=True)

    xbuf = io.BytesIO()
    with pd.ExcelWriter(xbuf, engine="openpyxl") as wr:
        df_cleaned.to_excel(wr, index=False, sheet_name="cleaned")
    st.download_button("💾 Download cleaned Excel (.xlsx)", data=xbuf.getvalue(),
                       file_name="cleaned.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)
