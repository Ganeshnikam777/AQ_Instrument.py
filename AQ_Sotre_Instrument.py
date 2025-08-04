import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Instrument Tracker", layout="centered")
st.title("🔧 Instrument Issue Tracker")

# File to store data
data_file = "instrument_data.csv"

# Load or create empty DataFrame
if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Instrument", "Quantity", "Issue Date", "Return Date", "Issued To"])
    df.to_csv(data_file, index=False)
else:
    df = pd.read_csv(data_file, parse_dates=["Issue Date", "Return Date"])

# --- Entry Form ---
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    instrument = col1.selectbox("Select Instrument", [
        "Ultrasonic Flowmeter", "Lux Meter", "Fluke Power Quality Analyzer",
        "Distance Gun", "eGauge", "Temperature Data Logger"
    ])
    quantity = col2.number_input("Quantity", min_value=1, step=1)
    issue_date = st.date_input("Issue Date", value=datetime.today())
    return_date = st.date_input("Return Date", value=datetime.today())
    issued_to = st.text_input("Issued To")

    submit = st.form_submit_button("📥 Save Entry")
    if submit:
        new_record = {
            "Instrument": instrument,
            "Quantity": quantity,
            "Issue Date": pd.to_datetime(issue_date),
            "Return Date": pd.to_datetime(return_date),
            "Issued To": issued_to
        }
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        df.to_csv(data_file, index=False)
        st.success("✅ Record saved successfully!")

# --- Display All Records ---
st.subheader("📋 All Records")
st.dataframe(df.sort_values(by="Issue Date", ascending=False), use_container_width=True)

# --- Filter by Month ---
st.subheader("📆 Filter Records by Month")
selected_month = st.date_input("Select Month", value=datetime.today())

filtered_df = df[
    (df['Issue Date'].dt.month == selected_month.month) &
    (df['Issue Date'].dt.year == selected_month.year)
]

if not filtered_df.empty:
    st.success(f"{len(filtered_df)} record(s) found for {selected_month.strftime('%B %Y')}")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("No records found for selected month.")


   
