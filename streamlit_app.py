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
                     
def calculate_kpis(df):
    """Calculate key performance indicators"""
    total_deliveries = len(df)
    on_time_count = len(df[df['on_time']])
    on_time_rate = (on_time_count / total_deliveries * 100) if total_deliveries > 0 else 0
    
    avg_delay = df[df['delay_minutes'] > 15]['delay_minutes'].mean()
    avg_delay = avg_delay if not pd.isna(avg_delay) else 0
    
    total_cost = df['delivery_cost'].sum()
    total_distance = df['distance_km'].sum()
    avg_rating = df['customer_rating'].mean()
    
    return {
        'total_deliveries': total_deliveries,
        'on_time_rate': round(on_time_rate, 1),
        'avg_delay': round(avg_delay, 1),
        'total_cost': round(total_cost/1000000, 1),
        'total_distance': round(total_distance/1000, 1),
        'avg_rating': round(avg_rating, 2) if not pd.isna(avg_rating) else 0
    }

# Load data
df = load_data()

# Set up input widgets
st.logo(image="images/streamlit-logo-primary-colormark-lighttext.png", 
        icon_image="images/streamlit-mark-color.png")

with st.sidebar:
    st.title("YouTube Channel Dashboard")
    st.header("⚙️ Settings")

    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    default_start_date = min_date
    default_end_date = max_date
    start_date = st.date_input("Start date", default_start_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=min_date, max_value=max_date)
    time_frame = st.selectbox("Select time frame",
                              ("Daily", "Weekly", "Monthly", "Quarterly"))

# Apply filters
filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

# Calculate KPIs
kpis = calculate_kpis(filtered_df)

# Display KPIs in cards
st.header("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📦 Total Deliveries",
        value=f"{kpis['total_deliveries']:,}",
        help="Total number of deliveries in selected period"
    )

with col2:
    st.metric(
        label="⏰ On-Time Rate",
        value=f"{kpis['on_time_rate']}%",
        delta=f"Target: 95%",
        help="Percentage of deliveries completed within 15 minutes of scheduled time"
    )

with col3:
    st.metric(
        label="🕐 Avg Delay",
        value=f"{kpis['avg_delay']:.0f} min",
        help="Average delay time for late deliveries"
    )

with col4:
    st.metric(
        label="⭐ Avg Rating",
        value=f"{kpis['avg_rating']:.1f}/5.0",
        help="Average customer satisfaction rating"
    )

# Additional KPIs row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Total Cost",
        value=f"${kpis['total_cost']:,.0f}M",
        help="Total delivery costs"
    )

with col2:
    st.metric(
        label="🛣️ Total Distance",
        value=f"{kpis['total_distance']:,.0f}K km",
        help="Total distance covered"
    )

with col3:
    cost_per_km = kpis['total_cost'] / kpis['total_distance'] if kpis['total_distance'] > 0 else 0
    st.metric(
        label="📏 Cost per KM",
        value=f"${cost_per_km:.2f}",
        help="Average cost per kilometer"
    )

with col4:
    deliveries_per_day = kpis['total_deliveries'] / len(filtered_df['date'].dt.date.unique())
    st.metric(
        label="📅 Daily Average",
        value=f"{deliveries_per_day:.1f}",
        help="Average deliveries per day"
    )
