import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os


# Page config
st.set_page_config(page_title="Instrument Tracker", layout="wide")
st.title("🔧 AQ Store - Instrument Tracker")

data_file = "instrument_data.csv"

# Predefined instrument list - add or edit as needed
instrument_list = [
    "Ultrasonic Flowmeter",
    "Lux Meter",
    "Fluke Power Quality Analyzer",
    "Distance Gun",
    "eGauge",
    "Temperature Data Logger"
]

# Load or create data
if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Instrument", "Quantity", "Issue Date", "Return Date", "Issued To"])
    df.to_csv(data_file, index=False)
else:
    df = pd.read_csv(data_file)

# Convert dates safely
df["Issue Date"] = pd.to_datetime(df["Issue Date"], errors="coerce")
df["Return Date"] = pd.to_datetime(df["Return Date"], errors="coerce")

# --- Entry form ---
st.sidebar.header("➕ Add New Instrument Issue")

with st.sidebar.form("add_instrument_form", clear_on_submit=True):
    issued_to = st.text_input("Issued To (Person's Name)", max_chars=50)
    instrument = st.selectbox("Select Instrument", options=instrument_list)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    issue_date = st.date_input("Issue Date", value=datetime.today())
    return_date = st.date_input("Return Date", value=datetime.today())
    submitted = st.form_submit_button("Add Entry")

if submitted:
    if not issued_to:
        st.sidebar.error("Please fill in the 'Issued To' field.")
    else:
        new_entry = {
            "Instrument": instrument,
            "Quantity": quantity,
            "Issue Date": pd.to_datetime(issue_date),
            "Return Date": pd.to_datetime(return_date),
            "Issued To": issued_to,
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(data_file, index=False)
        st.sidebar.success(f"Added entry: {instrument} issued to {issued_to}.")

        # Refresh date columns
        df["Issue Date"] = pd.to_datetime(df["Issue Date"], errors="coerce")
        df["Return Date"] = pd.to_datetime(df["Return Date"], errors="coerce")

# Remove rows with missing Issue Date
df = df[~df["Issue Date"].isna()]

# --- Filters ---
st.sidebar.header("🔍 Filter Records")

person_filter = st.sidebar.selectbox(
    "Filter by Issued To", options=["All"] + sorted(df["Issued To"].dropna().unique())
)

instrument_filter = st.sidebar.selectbox(
    "Filter by Instrument", options=["All"] + sorted(df["Instrument"].dropna().unique())
)

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

# Display filtered data
st.subheader("📋 Filtered Records")
st.dataframe(filtered_df, use_container_width=True)

# Excel export
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


