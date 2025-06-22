import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Train Delay & Accident Dashboard", layout="wide")

st.title("🚆 Indian Railway Delay & Accident Risk Dashboard")

# Load data
delay_data = pd.read_csv("train_delays.csv")
accident_data = pd.read_csv("train_accidents.csv")

# Section 1: Delay Summary
st.header("📊 Average Delay by Train")
top_delays = delay_data.groupby("train_name")["delay_minutes"].mean().sort_values(ascending=False).head(10)
st.bar_chart(top_delays)

# Section 2: Delay by Route
st.header("📍 Most Delayed Routes")
route_delay = delay_data.groupby(["source", "destination"])["delay_minutes"].mean().reset_index()
fig1 = px.scatter(route_delay, x="source", y="destination", size="delay_minutes",
                  color="delay_minutes", title="Route-wise Delay")
st.plotly_chart(fig1)

# Section 3: Accident Risk Map
st.header("🚨 High-Risk Accident Zones")
st.map(accident_data[['latitude', 'longitude']])

# Section 4: View Raw Data (optional)
with st.expander("📄 View Raw Delay Data"):
    st.dataframe(delay_data)

with st.expander("📄 View Accident Zone Data"):
    st.dataframe(accident_data)
