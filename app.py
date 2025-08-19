import streamlit as st
import pandas as pd

st.title("Data Cleaner")
st.write(
    "Upload a CSV or Excel file.\n"
    "• Drop rows that are completely empty.\n"
    "• Keep all columns (they will be filled, not dropped).\n"
    "   – String columns → 'N/A'\n"
    "   – Numeric columns → column mean\n"
)

uploaded_file = st.file_uploader(
    "Choose a file", type=["csv", "xls", "xlsx"]
)

if uploaded_file:
    # Detect file type and read accordingly
    if uploaded_file.name.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(uploaded_file)
    else:  # csv
        df = pd.read_csv(uploaded_file)

    st.write("Original data preview:", df.head())

    # 1️⃣ Drop rows that are all NaN
    df_cleaned = df.dropna(how="all")

    # 2️⃣ Fill each column
    for col in df_cleaned.columns:
        if pd.api.types.is_string_dtype(df_cleaned[col]):
            df_cleaned[col] = df_cleaned[col].fillna("N/A")
        else:   # numeric or other types
            mean_val = df_cleaned[col].mean()
            df_cleaned[col] = df_cleaned[col].fillna(mean_val)

    # 3️⃣ Drop duplicate rows after filling
    df_cleaned = df_cleaned.drop_duplicates()

    st.write("Cleaned data preview:", df_cleaned.head())

    # Convert back to the same format for download
    if uploaded_file.name.lower().endswith((".xls", ".xlsx")):
        # Excel requires a BytesIO buffer
        from io import BytesIO
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_cleaned.to_excel(writer, index=False)
        csv_bytes = buf.getvalue()
        file_ext = "xlsx"
    else:
        csv_bytes = df_cleaned.to_csv(index=False).encode("utf-8")
        file_ext = "csv"

    st.download_button(
        label="Download cleaned file",
    )
    