import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
import io

# Load environment variables
load_dotenv()

# Set the base URL for the FastAPI server
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY")

# Utility function to fetch data from the API
def fetch_data(endpoint, params=None):
    headers = {"access_token": API_KEY}
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code} {response.text}")
        return []

# Utility function to post data to the API
def post_data(endpoint, data=None):
    headers = {"access_token": API_KEY, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/{endpoint}", data=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to post data: {response.status_code} {response.text}")
        return None

# Utility function to format the fetched data into a DataFrame
def format_data(data):
    return pd.DataFrame(data)


def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to display data with pagination and sorting
def display_paginated_sorted_data(data, sort_by, sort_order, current_page=0, items_per_page=5):
    if sort_order == "Ascending":
        sorted_data = data.sort_values(by=sort_by, ascending=True)
    else:
        sorted_data = data.sort_values(by=sort_by, ascending=False)
    
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_data = sorted_data[start_idx:end_idx]
    st.dataframe(paginated_data)


# Sidebar filters
st.sidebar.header("Filters")

amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01)
if st.sidebar.button("Search by Amount"):
    data = fetch_data("transactions/search_by_amount", {"amount": amount})
    df = format_data(data)
    display_paginated_sorted_data(df, sort_by,sort_order,current_page,items_per_page )

start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")
if st.sidebar.button("Search by Date Range"):
    data = fetch_data("transactions/search_by_date_range", {"start_date": start_date, "end_date": end_date})
    df = format_data(data)
    display_paginated_sorted_data(df, sort_by,sort_order,current_page,items_per_page )

transaction_type = st.sidebar.selectbox("Transaction Type", ["WITHDRAW", "DEPOSIT", "TRANSFER", "EXTERNAL_PAYMENT", "REFUND", "OTHER"])
if st.sidebar.button("Search by Type"):
    data = fetch_data("transactions/search_by_type", {"type": transaction_type})
    df = format_data(data)
    display_paginated_sorted_data(df, sort_by,sort_order,current_page,items_per_page )

user_id = st.sidebar.text_input("User ID")
country = st.sidebar.text_input("Country")
if st.sidebar.button("Advanced Search"):
    params = {
        "amount": amount,
        "start_date": start_date,
        "end_date": end_date,
        "type": transaction_type,
        "user_id": user_id,
        "country": country
    }
    data = fetch_data("transactions/search_advanced", params)
    df = format_data(data)
    display_paginated_sorted_data(df, sort_by,sort_order,current_page,items_per_page )

# Sorting controls
sort_by = st.sidebar.selectbox("Sort By", ["origin_amount", "timestamp"])
sort_order = st.sidebar.selectbox("Sort Order", ["Ascending", "Descending"])

# Pagination controls
items_per_page = st.sidebar.number_input("Items per page", min_value=1, max_value=100, value=10)
current_page = st.sidebar.number_input("Page number", min_value=1, step=1, value=1)

# Main dashboard
st.title("Transaction Dashboard")

# Create transaction form
st.header("Create a New Transaction")
with st.form("transaction_form"):
    form_amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
    form_sender_id = st.text_input("Sender ID")
    form_destination_id = st.text_input("Destination ID")
    form_type = st.selectbox("Transaction Type", ["WITHDRAW", "DEPOSIT", "TRANSFER", "EXTERNAL_PAYMENT", "REFUND", "OTHER"])
    form_currency = st.text_input("Currency", value="USD")
    form_country = st.text_input("Country", value="US")
    submitted = st.form_submit_button("Create Transaction")

if submitted:
    transaction_data = {
        "amount": form_amount,
        "sender_id": form_sender_id,
        "destination_id": form_destination_id,
        "type": form_type,
        "currency": form_currency,
        "country": form_country,
    }
    result = post_data("create_transactions", transaction_data)
    if result:
        st.success("Transaction created successfully")


# Control CRON job
st.header("Control CRON Job")
if st.button("Start CRON Job"):
    result = post_data("cron/start")
    if result:
        st.success("CRON job started")

if st.button("Stop CRON Job"):
    result = post_data("cron/stop")
    if result:
        st.success("CRON job stopped")


# Generate transaction reports
st.header("Transaction Reports")
with st.form("report_form"):
    report_start_date = st.date_input("Report Start Date")
    report_end_date = st.date_input("Report End Date")
    report_submitted = st.form_submit_button("Generate Report")

if report_submitted:
    summary = fetch_data("transactions/summary", {"start_date": report_start_date, "end_date": report_end_date})
    total_amount = fetch_data("transactions/total_amount", {"start_date": report_start_date, "end_date": report_end_date})
    
    st.subheader("Transaction Summary")
    df_summary=format_data(summary)
    st.dataframe(format_data(summary))
    
    st.subheader("Total Transaction Amount")
    if total_amount:
        st.write(f"Total Transaction Amount: {total_amount['total_amount']}")
        
        
    csv_summary = convert_df_to_csv(df_summary)
    st.download_button(
        label="Download Transaction Summary as CSV",
        data=csv_summary,
        file_name='transaction_summary.csv',
        mime='text/csv',
    )