import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Indian Train Risk Dashboard", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    delay = pd.read_csv("Realistic_India_Train_Delays_2023_24.csv")
    accident = pd.read_csv("India_Train_Accidents_2000_2024.csv")

    delay['Scheduled Arrival'] = pd.to_datetime(delay['Scheduled Arrival'], errors='coerce')
    delay['Actual Arrival'] = pd.to_datetime(delay['Actual Arrival'], errors='coerce')
    delay.dropna(subset=['Train Name', 'Source', 'Destination', 'Delay (Minutes)'], inplace=True)

    return delay, accident

delay_df, accident_df = load_data()

# --- Sidebar Filters ---
st.sidebar.title("🚉 Filter Panel")

train_list = sorted(delay_df['Train Name'].unique().tolist())
selected_train = st.sidebar.selectbox("Select Train", ["All"] + train_list)

min_date = delay_df['Scheduled Arrival'].min()
max_date = delay_df['Scheduled Arrival'].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

# --- Apply Filters ---
filtered_delay = delay_df.copy()
if selected_train != "All":
    filtered_delay = filtered_delay[filtered_delay["Train Name"] == selected_train]

filtered_delay = filtered_delay[
    (filtered_delay["Scheduled Arrival"] >= pd.to_datetime(date_range[0])) &
    (filtered_delay["Scheduled Arrival"] <= pd.to_datetime(date_range[1]))
]

# --- Header ---
st.title("🚦 Indian Train Delay & Accident Risk Dashboard")

# --- Metrics ---
col1, col2, col3 = st.columns(3)
with col1:
    avg_delay = filtered_delay['Delay (Minutes)'].mean()
    st.metric("📉 Avg Delay (mins)", f"{avg_delay:.2f}" if not pd.isna(avg_delay) else "N/A")
with col2:
    st.metric("🚨 Total Accidents (2000–2024)", len(accident_df))
with col3:
    st.metric("🚆 Trains Monitored", filtered_delay['Train Name'].nunique())

st.markdown("---")

# --- Top Delayed Trains ---
st.subheader("📊 Top 10 Delayed Trains")
top_delay = (
    filtered_delay.groupby("Train Name")["Delay (Minutes)"]
    .mean().sort_values(ascending=False).head(10).reset_index()
)
fig1 = px.bar(top_delay, x="Train Name", y="Delay (Minutes)", color="Delay (Minutes)", title="Top Delayed Trains")
st.plotly_chart(fig1, use_container_width=True)

# --- Delay by Source City ---
st.subheader("📍 Delay by Source City")
city_delay = (
    filtered_delay.groupby("Source")["Delay (Minutes)"]
    .mean().sort_values(ascending=False).head(10).reset_index()
)
fig2 = px.bar(city_delay, x="Source", y="Delay (Minutes)", color="Delay (Minutes)")
st.plotly_chart(fig2, use_container_width=True)

# --- Accident Summary Table ---
st.subheader("📋 Train Accidents (2000–2024)")
st.dataframe(accident_df[['Year', 'Train Name', 'Departure From', 'Going To', 'Accident Location']], height=300)

# --- Raw Data View ---
with st.expander("🔍 View Raw Delay Data"):
    st.dataframe(filtered_delay)
