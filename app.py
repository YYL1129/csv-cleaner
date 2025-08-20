# app.py
import io
import pandas as pd
import streamlit as st
from pandas.api.types import is_string_dtype, is_numeric_dtype

st.set_page_config(page_title="CSV/Excel Cleaner", page_icon="🧽", layout="wide")
st.title("🧽 CSV/Excel Cleaner")

st.write(
    "Upload a CSV/XLSX/XLS file.\n"
    "• Drop rows that are completely empty.\n"
    "• Keep all columns (they will be filled, not dropped):\n"
    "   – String columns → 'N/A'\n"
    "   – Numeric columns → column mean\n"
    "• Then drop duplicate rows.\n"
)

uploaded_file = st.file_uploader("Choose a CSV, XLSX, or XLS file", type=["csv", "xlsx", "xls"])

def read_any_table(file) -> pd.DataFrame:
    name = file.name.lower()
    # --- CSV ---
    if name.endswith(".csv"):
        try:
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, encoding="latin-1")

    # --- Excel (xlsx/xls) ---
    # Try openpyxl (xlsx) first, then xlrd (xls)
    file.seek(0)
    try:
        # If multiple sheets, let user select one
        xls = pd.ExcelFile(file, engine="openpyxl")  # works for .xlsx
        sheet = st.selectbox("Select sheet", xls.sheet_names, index=0)
        return pd.read_excel(xls, sheet_name=sheet)
    except Exception:
        file.seek(0)
        try:
            xls = pd.ExcelFile(file, engine="xlrd")  # for legacy .xls
            sheet = st.selectbox("Select sheet", xls.sheet_names, index=0)
            return pd.read_excel(xls, sheet_name=sheet)
        except Exception as e:
            st.error(f"Could not read this Excel file. ({e})")
            st.stop()

if uploaded_file:
    df = read_any_table(uploaded_file)
    st.subheader("Original data (first 50 rows)")
    st.dataframe(df.head(50), use_container_width=True)

    # 1) Drop rows that are all NaN
    df_cleaned = df.dropna(how="all")

    # 2) Fill per column
    for col in df_cleaned.columns:
        if is_string_dtype(df_cleaned[col]):
            df_cleaned[col] = df_cleaned[col].fillna("N/A")
        elif is_numeric_dtype(df_cleaned[col]):
            mean_val = df_cleaned[col].mean()
            df_cleaned[col] = df_cleaned[col].fillna(mean_val)
        else:
            # leave other dtypes (dates/booleans/etc.) as-is
            pass

    # 3) Drop duplicate rows
    df_cleaned = df_cleaned.drop_duplicates()

    st.subheader("Cleaned data (first 50 rows)")
    st.dataframe(df_cleaned.head(50), use_container_width=True)

    # Metrics
    before_rows = len(df)
    after_rows = len(df_cleaned)
    removed_rows = before_rows - after_rows
    before_na = int(df.isna().sum().sum())
    after_na = int(df_cleaned.isna().sum().sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows removed (duplicates/empty)", removed_rows)
    c2.metric("Cells filled", before_na - after_na)
    c3.metric("Final rows", after_rows)

    # --- Downloads: CSV and Excel ---
    # CSV
    csv_bytes = df_cleaned.to_csv(index=False).encode("utf-8")
    st.download_button(
        "💾 Download cleaned CSV",
        data=csv_bytes,
        file_name="cleaned.csv",
        mime="text/csv",
        use_container_width=True
    )

    # Excel
    xbuf = io.BytesIO()
    with pd.ExcelWriter(xbuf, engine="openpyxl") as writer:
        df_cleaned.to_excel(writer, index=False, sheet_name="cleaned")
    st.download_button(
        "💾 Download cleaned Excel (.xlsx)",
        data=xbuf.getvalue(),
        file_name="cleaned.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
