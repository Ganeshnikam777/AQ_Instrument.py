import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Set page config
st.set_page_config(page_title="Instrument Tracker", layout="wide")

# Title
st.title("AQ Store - Instrument Tracker")

# Upload CSV
uploaded_file = st.file_uploader("Upload Instrument Tracker Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Convert 'Issue Date' column to datetime safely
    if 'Issue Date' in df.columns:
        df['Issue Date'] = pd.to_datetime(df['Issue Date'], errors='coerce')

    # Sidebar filters
    current_year = datetime.now().year
    selected_month = st.sidebar.date_input("Select Month", value=datetime.now()).replace(day=1)

    # Filter data based on selected month
    filtered_df = df[
        (df['Issue Date'].dt.year == selected_month.year) &
        (df['Issue Date'].dt.month == selected_month.month)
    ]

    # Display filtered data
    st.subheader(f"Issued Instruments - {selected_month.strftime('%B %Y')}")
    st.dataframe(filtered_df)

    # Download filtered data as Excel
    if not filtered_df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='FilteredData')
        st.download_button(
            label="📥 Download Excel",
            data=output.getvalue(),
            file_name=f"Instrument_Report_{selected_month.strftime('%b_%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No data found for the selected month.")
