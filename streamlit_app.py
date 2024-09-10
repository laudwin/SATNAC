import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio
from datetime import datetime, timedelta
import random

# South African Electricity Tariff
ELECTRICITY_TARIFF_ZAR_PER_KWH = 2.20  # Rands per kWh

# Heat treatment processes and their temperature ranges and durations (in minutes)
HEAT_TREATMENT_PROCESSES = {
    "Annealing": (800, 900, 3),
    "Quenching": (800, 900, 3),
    "Tempering": (150, 650, 3),
    "Normalizing": (850, 950, 3),
    "Hardening": (800, 900, 3)
}

# List of machine IDs
MACHINE_IDS = ["Machine-1", "Machine-2", "Machine-3", "Machine-4", "Machine-5"]

# Initialize DataFrames to store real-time and hourly data
machine_data_df = pd.DataFrame(columns=[
    "device_id", "timestamp", "heat_treatment_process", "temperature",
    "pressure", "humidity", "vibration", "electricity_consumption_kwh",
    "electricity_cost_zar", "consumption_evaluation", "status"
])

hourly_data_df = pd.DataFrame(columns=[
    "device_id", "hour", "total_consumption_kwh", "total_cost_zar"
])

# Function to simulate heat treatment process
def simulate_heat_treatment_process(machine_id):
    process = random.choice(list(HEAT_TREATMENT_PROCESSES.keys()))
    temperature_range, duration = HEAT_TREATMENT_PROCESSES[process][:2], HEAT_TREATMENT_PROCESSES[process][2]
    temperature = random.randint(*temperature_range)
    pressure = random.uniform(1.5, 3.0)
    electricity_consumption = random.uniform(10, 20) * (duration / 3)  # Adjust for duration
    cost = electricity_consumption * ELECTRICITY_TARIFF_ZAR_PER_KWH
    humidity = random.randint(30, 70)
    vibration = random.uniform(0.1, 2.0)
    evaluation = "Good" if electricity_consumption < 5 else "Moderate" if 5 <= electricity_consumption < 15 else "High"
    status = "Operating" if random.random() > 0.1 else "Idle" if random.random() > 0.5 else "Maintenance Required"
    
    return {
        "device_id": machine_id,
        "heat_treatment_process": process,
        "temperature": temperature,
        "pressure": pressure,
        "humidity": humidity,
        "vibration": vibration,
        "electricity_consumption_kwh": electricity_consumption,
        "electricity_cost_zar": round(cost, 2),
        "consumption_evaluation": evaluation,
        "status": status,
        "timestamp": datetime.now()
    }

# Streamlit App Layout
st.set_page_config(page_title="Real-Time Machine Monitoring Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #f4f4f9;
            color: #333;
            font-family: Arial, sans-serif;
        }
        .stButton>button {
            background-color: #007BFF;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .stSelectbox>div>div>div {
            background-color: #007BFF;
            color: white;
        }
        .stSelectbox>div>div>div>div>div {
            background-color: #007BFF;
            color: white;
        }
        .stMarkdown {
            font-size: 1.1em;
            color: #333;
        }
        .stApp {
            background-color: #f4f4f9;
        }
        .stSelectbox>div>div>div>div {
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Real-Time Machine Monitoring Dashboard")

# Create a select box for machine selection
selected_machine = st.selectbox("Select Machine", MACHINE_IDS)

# Create a dropdown for selecting the type of graph
graph_type = st.selectbox("Select Graph Type", [
    "Temperature vs. Time", 
    "Pressure, Humidity & Vibration", 
    "Electricity Consumption & Cost", 
    "Consumption Evaluation",
    "Hourly Electricity Consumption & Cost",
    "Machine Status"
])

# Create a button to refresh the data
if st.button("Refresh Data"):
    st.write("Data refreshed!")

# Placeholder for dynamic content
machine_placeholder = st.empty()
graph_placeholder = st.empty()

# Function to update machine data
async def update_machine_data():
    global machine_data_df, hourly_data_df
    while True:
        machine_data = simulate_heat_treatment_process(selected_machine)
        new_data = pd.DataFrame([machine_data])
        machine_data_df = pd.concat([machine_data_df, new_data], ignore_index=True)
        machine_data_df = machine_data_df.tail(50)  # Keep only the last 50 records for performance
        
        # Update hourly data
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        hourly_data = hourly_data_df[
            (hourly_data_df["device_id"] == selected_machine) &
            (hourly_data_df["hour"] == current_hour)
        ]
        
        if hourly_data.empty:
            hourly_data_df = pd.concat([
                hourly_data_df,
                pd.DataFrame([{
                    "device_id": selected_machine,
                    "hour": current_hour,
                    "total_consumption_kwh": machine_data["electricity_consumption_kwh"],
                    "total_cost_zar": machine_data["electricity_cost_zar"]
                }])
            ], ignore_index=True)
        else:
            hourly_data_df.loc[
                (hourly_data_df["device_id"] == selected_machine) &
                (hourly_data_df["hour"] == current_hour),
                "total_consumption_kwh"
            ] += machine_data["electricity_consumption_kwh"]
            hourly_data_df.loc[
                (hourly_data_df["device_id"] == selected_machine) &
                (hourly_data_df["hour"] == current_hour),
                "total_cost_zar"
            ] += machine_data["electricity_cost_zar"]

        # Filter data for the selected machine
        filtered_data = machine_data_df[machine_data_df["device_id"] == selected_machine]

        # Display machine information
        machine_placeholder.write(f"### Data for {selected_machine}")
        machine_placeholder.dataframe(filtered_data)

        # Plot based on selected graph type
        if graph_type == "Temperature vs. Time":
            fig_temp = px.line(filtered_data, x='timestamp', y='temperature', title='Temperature vs. Time',
                               labels={'timestamp': 'Time', 'temperature': 'Temperature (°C)'})
            graph_placeholder.plotly_chart(fig_temp, use_container_width=True)
        
        elif graph_type == "Pressure, Humidity & Vibration":
            fig_pressure_humidity_vibration = px.line(filtered_data, x='timestamp', y='pressure', title='Pressure, Humidity & Vibration vs. Time')
            fig_pressure_humidity_vibration.add_scatter(x=filtered_data['timestamp'], y=filtered_data['humidity'], mode='lines+markers', name='Humidity', marker=dict(color='orange'))
            fig_pressure_humidity_vibration.add_scatter(x=filtered_data['timestamp'], y=filtered_data['vibration'], mode='lines+markers', name='Vibration', marker=dict(color='green'))
            graph_placeholder.plotly_chart(fig_pressure_humidity_vibration, use_container_width=True)
        
        elif graph_type == "Electricity Consumption & Cost":
            fig_electricity = px.line(filtered_data, x='timestamp', y='electricity_consumption_kwh', title='Electricity Consumption & Cost',
                                      labels={'timestamp': 'Time', 'electricity_consumption_kwh': 'Consumption (kWh)'})
            fig_cost = px.line(filtered_data, x='timestamp', y='electricity_cost_zar', title='Electricity Cost',
                               labels={'timestamp': 'Time', 'electricity_cost_zar': 'Cost (ZAR)'})
            graph_placeholder.plotly_chart(fig_electricity, use_container_width=True)
            graph_placeholder.plotly_chart(fig_cost, use_container_width=True)
        
        elif graph_type == "Consumption Evaluation":
            status_counts = filtered_data['consumption_evaluation'].value_counts()
            fig_evaluation = px.pie(values=status_counts.values, names=status_counts.index, title='Consumption Evaluation Distribution')
            graph_placeholder.plotly_chart(fig_evaluation, use_container_width=True)
        
        elif graph_type == "Hourly Electricity Consumption & Cost":
            hourly_filtered_data = hourly_data_df[hourly_data_df["device_id"] == selected_machine]
            fig_hourly_consumption = px.line(hourly_filtered_data, x='hour', y='total_consumption_kwh', title='Hourly Electricity Consumption',
                                             labels={'hour': 'Hour', 'total_consumption_kwh': 'Consumption (kWh)'})
            fig_hourly_cost = px.line(hourly_filtered_data, x='hour', y='total_cost_zar', title='Hourly Electricity Cost',
                                      labels={'hour': 'Hour', 'total_cost_zar': 'Cost (ZAR)'})
            graph_placeholder.plotly_chart(fig_hourly_consumption, use_container_width=True)
            graph_placeholder.plotly_chart(fig_hourly_cost, use_container_width=True)

        elif graph_type == "Machine Status":
            status_counts = filtered_data['status'].value_counts()
            fig_status = px.pie(values=status_counts.values, names=status_counts.index, title='Machine Status Distribution')
            graph_placeholder.plotly_chart(fig_status, use_container_width=True)

        await asyncio.sleep(5)  # Update data every minute

# Start the async update loop
if st.button("Start Simulation"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_machine_data())
