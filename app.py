import streamlit as st
import pandas as pd

st.title("CSV Cleaner")
st.write(
    "Upload a CSV.\n"
    "• Drop rows that are completely empty.\n"
    "• Keep all columns (they will be filled, not dropped).\n"
    "   – String columns → 'N/A'\n"
    "   – Numeric columns → column mean\n"
)

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
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

    csv_bytes = df_cleaned.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download cleaned CSV",
        data=csv_bytes,
        file_name="cleaned.csv",
        mime="text/csv"
    )
