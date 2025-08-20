import streamlit as st
import pandas as pd
import io
from payment import render_paywall_and_check

st.set_page_config(page_title="CSV/Excel Cleaner", page_icon="🧽", layout="wide")

st.title("🧽 CSV/Excel Cleaner ✨")
st.write("Upload CSV/XLSX/XLS, choose cleaning mode, preview, and download.")

uploaded_file = st.file_uploader("Choose a CSV, XLSX, or XLS file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    # Load CSV or Excel
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    st.write(f"📊 Original data ({len(df)} rows, {len(df.columns)} columns)")
    st.dataframe(df.head(50), use_container_width=True)

    # Cleaning mode
    st.subheader("🛠 Choose Cleaning Mode")
    mode = st.radio("Select one:", [
        "🧹 Basic Cleaning – Remove blank rows & repeated rows",
        "✨ Smart Cleaning (Mean Fill) – Remove blanks, fill text → N/A, numbers → average",
        "🔢 Smart Cleaning (Zero Fill) – Remove blanks, fill text → N/A, numbers → 0",
    ])

    # Apply cleaning
    df_cleaned = df.copy()

    if mode == "🧹 Basic Cleaning – Remove blank rows & repeated rows":
        df_cleaned.dropna(how="all", inplace=True)
        df_cleaned.drop_duplicates(inplace=True)

    elif mode == "✨ Smart Cleaning (Mean Fill) – Remove blanks, fill text → N/A, numbers → average":
        df_cleaned.dropna(how="all", inplace=True)
        df_cleaned.drop_duplicates(inplace=True)
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == "object":
                df_cleaned[col].fillna("N/A", inplace=True)
            else:
                df_cleaned[col].fillna(df_cleaned[col].mean(), inplace=True)

    elif mode == "🔢 Smart Cleaning (Zero Fill) – Remove blanks, fill text → N/A, numbers → 0":
        df_cleaned.dropna(how="all", inplace=True)
        df_cleaned.drop_duplicates(inplace=True)
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype == "object":
                df_cleaned[col].fillna("N/A", inplace=True)
            else:
                df_cleaned[col].fillna(0, inplace=True)

    # Show summary
    before_rows = len(df)
    after_rows = len(df_cleaned)
    removed_rows = before_rows - after_rows

    st.metric("Rows before", before_rows)
    st.metric("Rows after", after_rows)
    st.metric("Rows removed", removed_rows)

    st.subheader("✅ Cleaned Data Preview")
    st.dataframe(df_cleaned.head(50), use_container_width=True)

    # --------------------
    # Paywall Check
    # --------------------
    can_download = render_paywall_and_check()

    csv_bytes = df_cleaned.to_csv(index=False).encode("utf-8")
    xbuf = io.BytesIO()
    with pd.ExcelWriter(xbuf, engine="openpyxl") as wr:
        df_cleaned.to_excel(wr, index=False, sheet_name="cleaned")

    if can_download:
        st.download_button("⬇️ Download CSV", data=csv_bytes, file_name="cleaned.csv", mime="text/csv", use_container_width=True)
        st.download_button("⬇️ Download Excel", data=xbuf.getvalue(), file_name="cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.warning("🔒 Download locked. Please enter your access code in the sidebar.")
