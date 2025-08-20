# app.py
import io
import pandas as pd
import streamlit as st
from pandas.api.types import is_string_dtype, is_numeric_dtype

st.set_page_config(page_title="CSV/Excel Cleaner", page_icon="🧽", layout="wide")
st.title("🧽 CSV/Excel Cleaner")

st.write(
    "Upload a CSV/XLSX/XLS file, choose a function, preview, then download."
)

# -------------------- File upload --------------------
uploaded_file = st.file_uploader("Choose a CSV, XLSX, or XLS file", type=["csv", "xlsx", "xls"])

def read_any_table(file) -> pd.DataFrame:
    name = file.name.lower()
    # CSV
    if name.endswith(".csv"):
        try:
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, encoding="latin-1")
    # Excel (xlsx/xls)
    file.seek(0)
    try:
        xls = pd.ExcelFile(file, engine="openpyxl")        # .xlsx
        sheet = st.selectbox("Select sheet", xls.sheet_names, index=0)
        return pd.read_excel(xls, sheet_name=sheet)
    except Exception:
        file.seek(0)
        xls = pd.ExcelFile(file, engine="xlrd")            # legacy .xls
        sheet = st.selectbox("Select sheet", xls.sheet_names, index=0)
        return pd.read_excel(xls, sheet_name=sheet)

# -------------------- Mode selection --------------------
st.markdown("### 🔧 Choose function")
mode = st.radio(
    "Select one:",
    [
        "1) Drop empty rows & duplicates",
        "2) Drop empty rows & duplicates, then fill empties (strings → 'N/A', numerics → mean())",
    ],
    index=0
)

if uploaded_file:
    df = read_any_table(uploaded_file)
    st.subheader("Original data (first 50 rows)")
    st.dataframe(df.head(50), use_container_width=True)

    # --- Step 1: drop rows that are all NaN
    df_cleaned = df.dropna(how="all")

    # --- Step 2: (optional) fill empties based on dtype
    if mode.startswith("2)"):
        for col in df_cleaned.columns:
            if is_string_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna("N/A")
            elif is_numeric_dtype(df_cleaned[col]):
                mean_val = df_cleaned[col].mean()
                df_cleaned[col] = df_cleaned[col].fillna(mean_val)
            else:
                # leave other dtypes (dates/booleans) unchanged
                pass

    # --- Step 3: drop exact duplicate rows
    df_cleaned = df_cleaned.drop_duplicates()

    # ---- Metrics
    before_rows = len(df)
    after_rows = len(df_cleaned)
    removed_rows = before_rows - after_rows
    before_na = int(df.isna().sum().sum())
    after_na = int(df_cleaned.isna().sum().sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows removed (empty/duplicates)", removed_rows)
    c2.metric("Cells filled", max(0, before_na - after_na))
    c3.metric("Final rows", after_rows)

    st.subheader("Cleaned data (first 50 rows)")
    st.dataframe(df_cleaned.head(50), use_container_width=True)

    # -------------------- Downloads --------------------
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
