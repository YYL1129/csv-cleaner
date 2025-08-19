import streamlit as st
import pandas as pd

st.title("CSV Cleaner")
st.write(
    "Upload a CSV. Choose whether you want to only drop empty rows/duplicates "
    "or also fill missing numeric values with the column mean."
)

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Original data preview:", df.head())

    # --- options ----------------------------------------------------
    option = st.radio(
        "What cleaning method?",
        ("Drop empty rows & duplicates only",
         "Drop empty rows, duplicates & mean‑fill numerics")
    )

    df_cleaned = df.dropna().drop_duplicates()

    if option == "Drop empty rows, duplicates & mean‑fill numerics":
        numeric_cols = df_cleaned.select_dtypes(include="number").columns
        for col in numeric_cols:
            df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())

    st.write("Cleaned data preview:", df_cleaned.head())
    # ----------------------------------------------------------------

    csv_bytes = df_cleaned.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download cleaned CSV",
        data=csv_bytes,
        file_name="cleaned.csv",
        mime="text/csv"
    )
