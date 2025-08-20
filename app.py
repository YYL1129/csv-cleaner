import streamlit as st
import pandas as pd

st.title("CSV / Excel Cleaner 🧹✨")
st.write(
    "Upload your CSV or Excel file. Choose how you want it cleaned."
)

uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("📄 Original data preview:", df.head())

    # Radio button with plain labels
    mode = st.radio(
        "Select cleaning method:",
        [
            "🧹 Basic Cleaning – Remove blank rows and repeated rows",
            "✨ Smart Cleaning – Remove blank & repeated rows, then fill missing data (text → N/A, numbers → average)"
        ],
        index=0
    )

    # Show example explanation
    if mode.startswith("🧹"):
        st.info("Example:\n\nBefore → Row 3 is completely empty, Row 5 is repeated\n\nAfter → These rows are removed ✅")
        # Example mini table
        example_before = pd.DataFrame({
            "Name": ["Alice", None, "Bob", "Bob"],
            "Age": [25, None, 30, 30]
        })
        example_after = example_before.dropna(how="all").drop_duplicates()
        st.write("Before:", example_before)
        st.write("After:", example_after)

    if mode.startswith("✨"):
        st.info("Example:\n\nBefore → Some cells are blank (Name, Age)\n\nAfter → Blank names filled with 'N/A', blank ages filled with column average ✅")
        example_before = pd.DataFrame({
            "Name": ["Alice", None, "Charlie"],
            "Age": [25, None, 40]
        })
        example_after = example_before.copy()
        example_after["Name"] = example_after["Name"].fillna("N/A")
        example_after["Age"] = example_after["Age"].fillna(example_after["Age"].mean())
        st.write("Before:", example_before)
        st.write("After:", example_after)

    # 🔧 Apply actual cleaning to uploaded file
    df_cleaned = df.dropna(how="all")  # drop completely empty rows

    if mode.startswith("🧹"):  # Basic
        df_cleaned = df_cleaned.drop_duplicates()

    elif mode.startswith("✨"):  # Smart
        for col in df_cleaned.columns:
            if pd.api.types.is_string_dtype(df_cleaned[col]):
                df_cleaned[col] = df_cleaned[col].fillna("N/A")
            else:
                mean_val = df_cleaned[col].mean()
                df_cleaned[col] = df_cleaned[col].fillna(mean_val)
        df_cleaned = df_cleaned.drop_duplicates()

    # Show cleaned preview
    st.write("✅ Cleaned data preview:", df_cleaned.head())

    # Download button
    file_ext = "csv" if uploaded_file.name.endswith(".csv") else "xlsx"
    if file_ext == "csv":
        output = df_cleaned.to_csv(index=False).encode("utf-8")
        mime = "text/csv"
    else:
        from io import BytesIO
        output_stream = BytesIO()
        df_cleaned.to_excel(output_stream, index=False, engine="xlsxwriter")
        output = output_stream.getvalue()
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    st.download_button(
        label=f"⬇️ Download cleaned {file_ext.upper()}",
        data=output,
        file_name=f"cleaned.{file_ext}",
        mime=mime
    )
