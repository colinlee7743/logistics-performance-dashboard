import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta, datetime

# Set page config
st.set_page_config(page_title="Logistics Dashboard", page_icon="🚛", layout="wide")

# Helper functions
@st.cache_data
def load_data():
    """Load and process the delivery data"""
    df = pd.read_csv("data/deliveries.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['on_time'] = df['delay_minutes'] <= 15
    return df

def custom_quarter(date):
    month = date.month
    year = date.year
    if month in [7, 8, 9]:        # Jul–Sep: Q1
      fiscal_year = year
      quarter = 1
    elif month in [10, 11, 12]:  # Oct–Dec: Q2
      fiscal_year = year
      quarter = 2
    elif month in [1, 2, 3]:     # Jan–Mar: Q3
      fiscal_year = year - 1
      quarter = 3
    else:                        # Apr–Jun: Q4
      fiscal_year = year - 1
      quarter = 4
      
    return pd.Period(year=fiscal_year, quarter=quarter, freq='Q')

# Load data
df = load_data()

# Set up input widgets
st.logo(image="images/streamlit-logo-primary-colormark-lighttext.png", 
        icon_image="images/streamlit-mark-color.png")

with st.sidebar:
    st.title("YouTube Channel Dashboard")
    st.header("⚙️ Settings")
    
    max_date = df['DATE'].max().date()
    default_start_date = max_date - timedelta(days=365)  # Show a year by default
    default_end_date = max_date
    start_date = st.date_input("Start date", default_start_date, min_value=df['DATE'].min().date(), max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=df['DATE'].min().date(), max_value=max_date)
    time_frame = st.selectbox("Select time frame",
                              ("Daily", "Weekly", "Monthly", "Quarterly"),
    )
    chart_selection = st.selectbox("Select a chart type",
                                   ("Bar", "Area"))
