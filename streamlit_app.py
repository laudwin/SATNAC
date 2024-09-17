import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import random

# South African Electricity Tariff and Carbon Emissions Factor
ELECTRICITY_TARIFF_ZAR_PER_KWH = 2.20  # Rands per kWh
CARBON_EMISSIONS_FACTOR = 0.9  # kg CO2 per kWh (example value)

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
machine_data_df = pd.DataFrame(columns=[  # Added 'carbon_emissions_kg' column
    "device_id", "timestamp", "heat_treatment_process", "temperature",
    "pressure", "humidity", "vibration", "electricity_consumption_kwh",
    "electricity_cost_zar", "carbon_emissions_kg", "consumption_evaluation",
    "status", "component_status", "component_failure_reason"
])

hourly_data_df = pd.DataFrame(columns=[  # Added 'total_emissions_kg' column
    "device_id", "hour", "total_consumption_kwh", "total_cost_zar", "total_emissions_kg"
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
    carbon_emissions = electricity_consumption * CARBON_EMISSIONS_FACTOR
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
        "carbon_emissions_kg": round(carbon_emissions, 2),
        "consumption_evaluation": evaluation,
        "status": status,
        "component_status": component_status,
        "component_failure_reason": component_failure_reason,
        "timestamp": datetime.now()
    }

# Streamlit App Layout
st.set_page_config(page_title="Real-Time Machine Monitoring Dashboard", layout="wide")

# Custom CSS
st.markdown("""  # 
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
    "Carbon Emissions & Cost", 
    "Consumption Evaluation",
    "Hourly Electricity Consumption & Cost",
    "Hourly Carbon Emissions & Cost",
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
                    "total_cost_zar": machine_data["electricity_cost_zar"],
                    "total_emissions_kg": machine_data["carbon_emissions_kg"]
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
            hourly_data_df.loc[
                (hourly_data_df["device_id"] == selected_machine) &
                (hourly_data_df["hour"] == current_hour),
                "total_emissions_kg"
            ] += machine_data["carbon_emissions_kg"]

        # Filter data for the selected machine
        filtered_data = machine_data_df[machine_data_df["device_id"] == selected_machine]

        # Display machine information
        machine_placeholder.write(f"### Data for {selected_machine}")
        machine_placeholder.dataframe(filtered_data)

        # Plot based on selected graph type
        if graph_type == "Temperature vs. Time":
            fig = px.line(filtered_data, x="timestamp", y="temperature", title="Temperature vs. Time")
        elif graph_type == "Pressure, Humidity & Vibration":
            fig = px.line(filtered_data, x="timestamp", y=["pressure", "humidity", "vibration"], title="Pressure, Humidity & Vibration")
        elif graph_type == "Electricity Consumption & Cost":
            fig = px.line(filtered_data, x="timestamp", y=["electricity_consumption_kwh", "electricity_cost_zar"], title="Electricity Consumption & Cost")
        elif graph_type == "Carbon Emissions & Cost":
            fig = px.line(filtered_data, x="timestamp", y=["carbon_emissions_kg", "electricity_cost_zar"], title="Carbon Emissions & Cost")
        elif graph_type == "Consumption Evaluation":
            fig = px.pie(filtered_data, names="consumption_evaluation", title="Consumption Evaluation")
        elif graph_type == "Hourly Electricity Consumption & Cost":
            hourly_summary = hourly_data_df[hourly_data_df["device_id"] == selected_machine]
            fig = px.bar(hourly_summary, x="hour", y=["total_consumption_kwh", "total_cost_zar"], title="Hourly Electricity Consumption & Cost")
        elif graph_type == "Hourly Carbon Emissions & Cost":
            hourly_summary = hourly_data_df[hourly_data_df["device_id"] == selected_machine]
            fig = px.bar(hourly_summary, x="hour", y=["total_emissions_kg", "total_cost_zar"], title="Hourly Carbon Emissions & Cost")
        elif graph_type == "Machine Status":
            status_counts = filtered_data["status"].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, title="Machine Status Distribution")
        elif graph_type == "Pie Chart of Machine Temperatures":
            fig = px.pie(filtered_data, names="temperature", title="Pie Chart of Machine Temperatures")
        elif graph_type == "Bar Chart of Electricity Consumption and Costs":
            fig = px.bar(filtered_data, x="timestamp", y=["electricity_consumption_kwh", "electricity_cost_zar"], title="Bar Chart of Electricity Consumption and Costs")
        elif graph_type == "Line Chart of Temperature Trends Over Time":
            fig = px.line(filtered_data, x="timestamp", y="temperature", title="Line Chart of Temperature Trends Over Time")
        elif graph_type == "Heatmap of Temperature Differences":
            # Calculating temperature differences for the heatmap
            filtered_data['temp_diff'] = filtered_data['temperature'].diff().fillna(0)
            fig = px.imshow(filtered_data.pivot_table(index='timestamp', values='temp_diff'), title="Heatmap of Temperature Differences")

        graph_placeholder.plotly_chart(fig)
        
        time.sleep(5)  # Update every 5 seconds

# Start the simulation
update_machine_data()
