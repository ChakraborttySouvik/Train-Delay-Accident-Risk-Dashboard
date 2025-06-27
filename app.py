import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Train Risk Dashboard", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    delay = pd.read_csv("Realistic_India_Train_Delays_2023_24.csv")
    accident = pd.read_csv("India_Train_Accidents_2000_2024.csv")
    delay['date'] = pd.to_datetime(delay['date'], errors='coerce')
    return delay, accident

delay_df, accident_df = load_data()

# --- Sidebar Filters ---
st.sidebar.title("🚉 Filters")

# Handle missing or invalid train names
unique_trains = delay_df['train_name'].dropna().unique()
selected_train = st.sidebar.selectbox("Select Train", ["All"] + sorted(unique_trains.tolist()))

# Date filter
valid_dates = delay_df['date'].dropna()
if not valid_dates.empty:
    min_date = valid_dates.min()
    max_date = valid_dates.max()
else:
    min_date = max_date = pd.Timestamp.today()

date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Severity filter
severity_filter = st.sidebar.multiselect("Accident Severity", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])

# --- Filtering Data ---
filtered_delay = delay_df.copy()
if selected_train != "All":
    filtered_delay = filtered_delay[filtered_delay['train_name'] == selected_train]

filtered_delay = filtered_delay[
    (filtered_delay['date'] >= pd.to_datetime(date_range[0])) &
    (filtered_delay['date'] <= pd.to_datetime(date_range[1]))
]

filtered_accidents = accident_df[accident_df['severity'].isin(severity_filter)]

# --- Header ---
st.title("🚦 Indian Train Delay & Accident Risk Dashboard")
st.markdown("Track average delays and visualize accident hotspots in India’s train system.")

# --- KPIs ---
col1, col2, col3 = st.columns(3)
with col1:
    avg_delay = round(filtered_delay['delay_minutes'].mean(), 1) if not filtered_delay.empty else 0
    st.metric("📉 Avg Delay (mins)", avg_delay)
with col2:
    st.metric("🚨 Accidents", len(filtered_accidents))
with col3:
    st.metric("🚆 Trains Monitored", filtered_delay['train_name'].nunique())

st.markdown("---")

# --- Delay Chart ---
if not filtered_delay.empty:
    st.subheader("📊 Top Delayed Trains")
    top_delayed = filtered_delay.groupby("train_name")["delay_minutes"].mean().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(top_delayed, x="train_name", y="delay_minutes", color="delay_minutes", title="Top 10 Most Delayed Trains")
    st.plotly_chart(fig1, use_container_width=True)

    # --- Delay by City ---
    st.subheader("📍 Delay by Source Station")
    delay_by_city = filtered_delay.groupby("source_station")["delay_minutes"].mean().reset_index()
    fig2 = px.bar(delay_by_city.sort_values("delay_minutes", ascending=False).head(10),
                  x="source_station", y="delay_minutes", color="delay_minutes")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No delay data available for selected filters.")

# --- Accident Map ---
if not filtered_accidents.empty and {'latitude', 'longitude'}.issubset(filtered_accidents.columns):
    st.subheader("🗺️ Accident Hotspots Map")
    st.map(filtered_accidents[['latitude', 'longitude']])
else:
    st.warning("No valid accident location data available.")

# --- Expandable Raw Data ---
with st.expander("📄 View Raw Delay Data"):
    st.dataframe(filtered_delay)

with st.expander("📄 View Raw Accident Data"):
    st.dataframe(filtered_accidents)
