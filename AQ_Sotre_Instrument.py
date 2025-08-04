import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

st.set_page_config(page_title="Instrument Tracker", layout="centered")
st.title("🔧 Instrument Issue Tracker")

# File to store records
data_file = "instrument_data.csv"

# Initialize empty DataFrame if file does not exist
if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Instrument", "Quantity", "Issue Date", "Return Date", "Issued To"])
    df.to_csv(data_file, index=False)
else:
    df = pd.read_csv(data_file, parse_dates=["Issue Date", "Return Date"])

# --- Input Form ---
with st.form("data_entry_form"):
    col1, col2 = st.columns(2)
    instrument = col1.selectbox("Select Instrument", [
        "Ultrasonic Flowmeter", "Lux Meter", "Fluke Power Quality Analyzer",
        "Distance Gun", "eGauge", "Temperature Data Logger"
    ])
    quantity = col2.number_input("Quantity", min_value=1, step=1)
    issue_date = st.date_input("Issue Date", value=datetime.today())
    return_date = st.date_input("Return Date", value=datetime.today())
    issued_to = st.text_input("Issued To")

    submitted = st.form_submit_button("📥 Save Entry")

    if submitted:
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

# --- Display Records ---
st.subheader("📋 All Records")
st.dataframe(df.sort_values(by="Issue Date", ascending=False), use_container_width=True)

# --- Filter by Month ---
st.subheader("📆 Generate Monthly Report")
selected_month = st.date_input("Select Month", value=datetime.today())

filtered_df = df[
    (df['Issue Date'].dt.month == selected_month.month) &
    (df['Issue Date'].dt.year == selected_month.year)
]

# --- PDF Report Function ---
def generate_pdf(data, month):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    title = f"Instrument Issue Report - {month.strftime('%B %Y')}"
    pdf.cell(200, 10, txt=title, ln=True, align="C")
    pdf.ln(10)

    for _, row in data.iterrows():
        line = (
            f"{row['Issue Date'].date()} - {row['Instrument']} x{row['Quantity']} "
            f"issued to {row['Issued To']} (Return by {row['Return Date'].date()})"
        )
        pdf.multi_cell(0, 10, txt=line)

    pdf_file = f"monthly_report_{month.strftime('%Y_%m')}.pdf"
    pdf.output(pdf_file)
    return pdf_file

# --- Show PDF Button if data exists ---
if not filtered_df.empty:
    st.success(f"{len(filtered_df)} record(s) found for {selected_month.strftime('%B %Y')}")
    if st.button("📄 Download Monthly PDF Report"):
        pdf_path = generate_pdf(filtered_df, selected_month)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name=pdf_path, mime="application/pdf")
else:
    st.info("No records found for selected month.")
