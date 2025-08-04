import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

# Page config
st.set_page_config(page_title="Instrument Tracker", layout="wide")
st.title("🔧 AQ Store - Instrument Tracker")

# Data file path
data_file = "instrument_data.csv"

# Load data or create empty CSV if not exists
if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Instrument", "Quantity", "Issue Date", "Return Date", "Issued To"])
    df.to_csv(data_file, index=False)
else:
    df = pd.read_csv(data_file)

# Convert dates safely
df["Issue Date"] = pd.to_datetime(df["Issue Date"], errors="coerce")
df["Return Date"] = pd.to_datetime(df["Return Date"], errors="coerce")

# Remove rows where Issue Date is NaT (optional: you can keep if you want)
df = df[~df["Issue Date"].isna()]

# Sidebar filters
st.sidebar.header("🔍 Filter Records")

person_filter = st.sidebar.selectbox(
    "Filter by Issued To", options=["All"] + sorted(df["Issued To"].dropna().unique())
)

instrument_filter = st.sidebar.selectbox(
    "Filter by Instrument", options=["All"] + sorted(df["Instrument"].dropna().unique())
)

# Handle NaT safely for date_input
valid_issue_dates = df["Issue Date"].dropna()
if not valid_issue_dates.empty:
    min_date = valid_issue_dates.min().date()
    max_date = valid_issue_dates.max().date()
else:
    min_date = max_date = datetime.today().date()

date_range = st.sidebar.date_input(
    "Filter by Issue Date Range",
    value=[min_date, max_date]
)

# Apply filters
filtered_df = df.copy()

if person_filter != "All":
    filtered_df = filtered_df[filtered_df["Issued To"] == person_filter]

if instrument_filter != "All":
    filtered_df = filtered_df[filtered_df["Instrument"] == instrument_filter]

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range)
    filtered_df = filtered_df[
        (filtered_df["Issue Date"] >= start_date) & (filtered_df["Issue Date"] <= end_date)
    ]

# Show filtered data
st.subheader("📋 Filtered Records")
st.dataframe(filtered_df, use_container_width=True)

# Excel download button with safe filename
if not filtered_df.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="FilteredData")

    report_date = datetime.now().strftime("%Y-%m-%d")
    st.download_button(
        label="📥 Download Excel Report",
        data=output.getvalue(),
        file_name=f"Instrument_Report_{report_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("No data to display or export. Please adjust your filters.")
