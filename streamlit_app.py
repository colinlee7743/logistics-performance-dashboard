import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta, datetime

# Set page config
st.set_page_config(page_title="Logistics Dashboard", page_icon="🚛", layout="wide")

# Reference - https://github.com/dataprofessor/dashboard-kit/blob/master/streamlit_app.py

# Helper functions
@st.cache_data
def load_data():
    """Load and process the delivery data"""
    df = pd.read_csv("data/deliveries.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['on_time'] = df['delay_minutes'] <= 15

    # Add time grouping columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['week'] = df['date'].dt.isocalendar().week
    df['day_of_week'] = df['date'].dt.day_name()
    df['month_year'] = df['date'].dt.to_period('M').astype(str)
    df['week_year'] = df['date'].dt.to_period('W').apply(lambda p: p.start_time.strftime('%Y-%m-%d')) # Show starting day only

    # Fiscal year (July-June) and Fiscal quarter
    df['fiscal_year'] = df['date'].apply(lambda x: x.year if x.month >= 7 else x.year - 1)
    def fiscal_quarter(month):
        if month in [7, 8, 9]:
            return 'Q1'
        elif month in [10, 11, 12]:
            return 'Q2'
        elif month in [1, 2, 3]:
            return 'Q3'
        else:  # Apr–Jun
            return 'Q4'

    df['fiscal_quarter'] = df['date'].dt.month.apply(fiscal_quarter)
    
    return df

def get_aggregated_data(df, grouping='Daily'):
    """Aggregate data by selected time period in a scalable way""" 
    # Define the aggregation logic
    agg_dict = {
        'delivery_id': 'count',
        'on_time': 'mean',
        'delay_minutes': 'mean',
        'delivery_cost': 'sum',
        'fuel_cost': 'sum',
        'distance_km': 'sum',
        'customer_rating': 'mean'
    }

    # Column rename mapping
    col_rename = {
        'delivery_id': 'Total_Deliveries',
        'on_time': 'On_Time_Rate',
        'delay_minutes': 'Avg_Delay',
        'delivery_cost': 'Total_Cost',
        'fuel_cost': 'Total_Fuel',
        'distance_km': 'Total_Distance',
        'customer_rating': 'Avg_Rating'
    }

    # Define group-by keys per grouping type
    group_keys = {
        'Daily': ['date'],
        'Weekly': ['week_year'],
        'Monthly': ['month_year'],
        'Quarterly': ['fiscal_year', 'fiscal_quarter']
    }

    if grouping not in group_keys:
        raise ValueError(f"Unsupported grouping: {grouping}")

    # Group and aggregate
    grouped = df.groupby(group_keys[grouping]).agg(agg_dict).reset_index()
    
    # Handle 'Period' column
    if grouping == 'Quarterly':
        grouped['Period'] = grouped['fiscal_year'].astype(str) + '-' + grouped['fiscal_quarter']
        grouped = grouped.drop(['fiscal_year', 'fiscal_quarter'], axis=1)
    else:
        grouped = grouped.rename(columns={group_keys[grouping][0]: 'Period'})
        
    # Rename metric columns
    grouped = grouped.rename(columns=col_rename)

    # Reorder columns
    metric_cols = list(col_rename.values())
    final_columns = ['Period'] + metric_cols
    grouped = grouped[final_columns]

    # Convert percentages and round numbers
    grouped['On_Time_Rate'] = (grouped['On_Time_Rate'] * 100).round(1)
    grouped['Avg_Delay'] = grouped['Avg_Delay'].round(1)
    grouped['Total_Cost'] = grouped['Total_Cost'].round(2)
    grouped['Total_Fuel'] = grouped['Total_Fuel'].round(2)
    grouped['Total_Distance'] = grouped['Total_Distance'].round(1)
    grouped['Avg_Rating'] = grouped['Avg_Rating'].round(2)
    
    return grouped
                     
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
        'total_cost': round(total_cost, 1),
        'total_distance': round(total_distance, 1),
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
    time_frame = st.selectbox(
        "Select time frame",
        options = ["Daily", "Weekly", "Monthly", "Quarterly"],
        index=2,  # Default to monthly,
        help="Choose how to aggregate the data for trend analysis"
    )

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
        value=f"${kpis['total_cost']/1000000:,.1f}M",
        help="Total delivery costs"
    )

with col2:
    st.metric(
        label="🛣️ Total Distance",
        value=f"{kpis['total_distance']/1000:,.0f}K km",
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

# Charts section
st.header("📈 {time_frame} Performance Analytics")

# Get grouped data once
grouped_data = get_aggregated_data(filtered_df, grouping=time_frame)
grouped_data.set_index('Period', inplace=True)

# Row 1: Trend and Driver Performance
col1, col2 = st.columns(2)

with col1:
    # Bar chart: Number of deliveries by period
    st.subheader(f"📦 Number of Deliveries")
    st.bar_chart(grouped_data['Total_Deliveries'])  # this directly renders it
    
with col2:
    st.subheader(f"⏰ On-Time Rate (%)")
    st.line_chart(grouped_data['On_Time_Rate'])
