import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
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
    "electricity_cost_zar", "consumption_evaluation", "status", "component_status", "component_failure_reason"
])

hourly_data_df = pd.DataFrame(columns=[
    "device_id", "hour", "total_consumption_kwh", "total_cost_zar"
])

# Function to simulate heat treatment process
def simulate_heat_treatment_process(machine_id, override_temperature=None):
    process = random.choice(list(HEAT_TREATMENT_PROCESSES.keys()))
    temperature_range, duration = HEAT_TREATMENT_PROCESSES[process][:2], HEAT_TREATMENT_PROCESSES[process][2]

    # If override_temperature is provided, use it; otherwise, generate a random temperature
    if override_temperature is not None:
        temperature = override_temperature
    else:
        temperature = random.randint(*temperature_range)

    pressure = random.uniform(1.5, 3.0)
    electricity_consumption = random.uniform(10, 20) * (duration / 3)  # Adjust for duration
    cost = electricity_consumption * ELECTRICITY_TARIFF_ZAR_PER_KWH
    humidity = random.randint(30, 70)
    vibration = random.uniform(0.1, 2.0)
    evaluation = "Good" if electricity_consumption < 5 else "Moderate" if 5 <= electricity_consumption < 15 else "High"
    status = "Operating" if random.random() > 0.1 else "Idle" if random.random() > 0.5 else "Maintenance Required"
    
    # Check if the temperature meets the standard
    min_temp, max_temp = temperature_range
    if min_temp <= temperature <= max_temp:
        component_status = "Pass"
        component_failure_reason = "Temperature within the standard range."
    else:
        component_status = "Fail"
        component_failure_reason = "Temperature outside the standard range. Components may fail due to insufficient or excessive heat."
    
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
        "component_status": component_status,
        "component_failure_reason": component_failure_reason,
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

# Create a slider for manual temperature adjustment
temperature_slider = st.slider(
    "Adjust Temperature (°C)", 
    min_value=100, 
    max_value=1000, 
    value=500
)

# Create a checkbox to enable or disable the slider's effect
override_temp = st.checkbox("Override with slider temperature", value=False)

# Create a dropdown for selecting the type of graph
graph_type = st.selectbox("Select Graph Type", [
    "Temperature vs. Time", 
    "Pressure, Humidity & Vibration", 
    "Electricity Consumption & Cost", 
    "Consumption Evaluation",
    "Hourly Electricity Consumption & Cost",
    "Machine Status",
    "Pie Chart of Machine Temperatures",
    "Bar Chart of Electricity Consumption and Costs",
    "Line Chart of Temperature Trends Over Time",
    "Heatmap of Temperature Differences"
])

# Placeholder for dynamic content
machine_placeholder = st.empty()
graph_placeholder = st.empty()

# Function to update machine data
def update_machine_data():
    global machine_data_df, hourly_data_df
    while True:
        # Use the slider's value if override is enabled; otherwise, set to None for automatic simulation
        override_temperature = temperature_slider if override_temp else None
        
        machine_data = simulate_heat_treatment_process(selected_machine, override_temperature)
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
            fig_electricity = px.line(filtered_data, x='timestamp', y='electricity_consumption_kwh', title='Electricity Consumption (kWh)',
                                     labels={'timestamp': 'Time', 'electricity_consumption_kwh': 'Consumption (kWh)'})
            fig_cost = px.line(filtered_data, x='timestamp', y='electricity_cost_zar', title='Electricity Cost (ZAR)',
                               labels={'timestamp': 'Time', 'electricity_cost_zar': 'Cost (ZAR)'})
            graph_placeholder.plotly_chart(fig_electricity, use_container_width=True)
            graph_placeholder.plotly_chart(fig_cost, use_container_width=True)
        
        elif graph_type == "Consumption Evaluation":
            fig_eval = px.bar(filtered_data, x='timestamp', y='consumption_evaluation', title='Consumption Evaluation',
                              labels={'timestamp': 'Time', 'consumption_evaluation': 'Evaluation'})
            graph_placeholder.plotly_chart(fig_eval, use_container_width=True)
        
        elif graph_type == "Hourly Electricity Consumption & Cost":
            hourly_data = hourly_data_df[hourly_data_df['device_id'] == selected_machine]
            fig_hourly = px.bar(hourly_data, x='hour', y='total_consumption_kwh', title='Hourly Electricity Consumption & Cost',
                                labels={'hour': 'Hour', 'total_consumption_kwh': 'Total Consumption (kWh)'})
            graph_placeholder.plotly_chart(fig_hourly, use_container_width=True)
        
        elif graph_type == "Machine Status":
            fig_status = px.bar(filtered_data, x='timestamp', y='status', title='Machine Status Over Time',
                                labels={'timestamp': 'Time', 'status': 'Status'})
            graph_placeholder.plotly_chart(fig_status, use_container_width=True)

        elif graph_type == "Pie Chart of Machine Temperatures":
            fig_pie_temp = px.pie(filtered_data, values='temperature', names='heat_treatment_process',
                                  title='Pie Chart of Machine Temperatures')
            graph_placeholder.plotly_chart(fig_pie_temp, use_container_width=True)
        
        elif graph_type == "Bar Chart of Electricity Consumption and Costs":
            fig_bar_cost = px.bar(filtered_data, x='timestamp', y=['electricity_consumption_kwh', 'electricity_cost_zar'],
                                  title='Bar Chart of Electricity Consumption and Costs')
            graph_placeholder.plotly_chart(fig_bar_cost, use_container_width=True)
        
        elif graph_type == "Line Chart of Temperature Trends Over Time":
            fig_line_temp = px.line(filtered_data, x='timestamp', y='temperature', title='Line Chart of Temperature Trends Over Time')
            graph_placeholder.plotly_chart(fig_line_temp, use_container_width=True)
        
        elif graph_type == "Heatmap of Temperature Differences":
            fig_heatmap_temp = px.density_heatmap(filtered_data, x='timestamp', y='temperature', title='Heatmap of Temperature Differences')
            graph_placeholder.plotly_chart(fig_heatmap_temp, use_container_width=True)
        
        # Sleep for 5 seconds before refreshing data
        time.sleep(5)

# Start the data simulation and dashboard update
update_machine_data()
