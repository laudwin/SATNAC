import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import random

# Constants
ELECTRICITY_TARIFF_ZAR_PER_KWH = 2.20
CARBON_EMISSIONS_FACTOR = 0.9

HEAT_TREATMENT_PROCESSES = {
    "Annealing": (800, 900, 3),
    "Quenching": (800, 900, 3),
    "Tempering": (150, 650, 3),
    "Normalizing": (850, 950, 3),
    "Hardening": (800, 900, 3)
}

MACHINE_IDS = ["Machine-1", "Machine-2", "Machine-3", "Machine-4", "Machine-5"]

machine_data_df = pd.DataFrame(columns=[  
    "device_id", "timestamp", "heat_treatment_process", "temperature",
    "pressure", "humidity", "vibration", "electricity_consumption_kwh",
    "electricity_cost_zar", "carbon_emissions_kg", "consumption_evaluation",
    "status", "component_status", "component_failure_reason"
])

hourly_data_df = pd.DataFrame(columns=[  
    "device_id", "hour", "total_consumption_kwh", "total_cost_zar", "total_emissions_kg"
])

def simulate_heat_treatment_process(machine_id, override_temperature=None):
    process = random.choice(list(HEAT_TREATMENT_PROCESSES.keys()))
    temperature_range, duration = HEAT_TREATMENT_PROCESSES[process][:2], HEAT_TREATMENT_PROCESSES[process][2]

    if override_temperature is not None:
        temperature = override_temperature
    else:
        temperature = random.randint(*temperature_range)

    pressure = random.uniform(1.5, 3.0)
    electricity_consumption = random.uniform(10, 20) * (duration / 3)
    cost = electricity_consumption * ELECTRICITY_TARIFF_ZAR_PER_KWH
    carbon_emissions = electricity_consumption * CARBON_EMISSIONS_FACTOR
    humidity = random.randint(30, 70)
    vibration = random.uniform(0.1, 2.0)
    evaluation = "Good" if electricity_consumption < 5 else "Moderate" if 5 <= electricity_consumption < 15 else "High"
    status = "Operating" if random.random() > 0.1 else "Idle" if random.random() > 0.5 else "Maintenance Required"
    
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
st.markdown(""" ... """, unsafe_allow_html=True)

# Title
st.title("Real-Time Machine Monitoring Dashboard")

# User Profile Section (Role-Based)
st.sidebar.title("User Profile")
operator_name = st.sidebar.text_input("Operator Name", value="Lesiba Mojela")
operator_id = st.sidebar.text_input("Operator ID", value="OP-22300")
operator_role = st.sidebar.selectbox("Role", ["Operator", "Supervisor", "Manager", "Technician"])
operator_shift = st.sidebar.selectbox("Shift", ["Morning", "Afternoon", "Night"])

st.sidebar.write(f"**Name:** {operator_name}")
st.sidebar.write(f"**ID:** {operator_id}")
st.sidebar.write(f"**Role:** {operator_role}")
st.sidebar.write(f"**Shift:** {operator_shift}")

st.sidebar.markdown("---")

selected_machine = st.selectbox("Select Machine", MACHINE_IDS)
temperature_slider = st.slider("Adjust Temperature (°C)", min_value=100, max_value=1000, value=500)
override_temp = st.checkbox("Override with slider temperature", value=False)
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
def update_machine_data():
    global machine_data_df, hourly_data_df
    while True:
        override_temperature = temperature_slider if override_temp else None
        machine_data = simulate_heat_treatment_process(selected_machine, override_temperature)
        new_data = pd.DataFrame([machine_data])
        machine_data_df = pd.concat([machine_data_df, new_data], ignore_index=True)
        machine_data_df = machine_data_df.tail(50)
        
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

        filtered_data = machine_data_df[machine_data_df["device_id"] == selected_machine]

        # Ensure numeric data types for plotting
        filtered_data["temperature"] = pd.to_numeric(filtered_data["temperature"], errors='coerce')
        filtered_data["pressure"] = pd.to_numeric(filtered_data["pressure"], errors='coerce')
        filtered_data["humidity"] = pd.to_numeric(filtered_data["humidity"], errors='coerce')
        filtered_data["vibration"] = pd.to_numeric(filtered_data["vibration"], errors='coerce')

        # Display role-specific data
        if operator_role == "Operator":
            st.sidebar.write("**Operator View:**")
            st.sidebar.write("Monitoring the machine's current status and settings.")
            # Display machine status, detailed logs, and all available data
            machine_placeholder.write(filtered_data.tail(10))

        elif operator_role == "Technician":
            st.sidebar.write("**Technician View:**")
            st.sidebar.write("Detailed component status and potential issues.")
            # Display detailed component status, failure reasons, and machine data for maintenance
            machine_placeholder.write(filtered_data[['timestamp', 'heat_treatment_process', 'temperature', 'pressure', 'humidity', 'vibration', 'status', 'component_status', 'component_failure_reason']].tail(10))

        elif operator_role == "Supervisor":
            st.sidebar.write("**Supervisor View:**")
            st.sidebar.write("Performance and efficiency metrics.")
            # Display performance metrics, efficiency, and decision-making data
            machine_placeholder.write(filtered_data[['timestamp', 'electricity_consumption_kwh', 'electricity_cost_zar', 'consumption_evaluation']].tail(10))

        elif operator_role == "Manager":
            st.sidebar.write("**Manager View:**")
            st.sidebar.write("Cost, consumption, and overall performance.")
            # Display high-level business-impacting data
            machine_placeholder.write(filtered_data[['timestamp', 'electricity_consumption_kwh', 'electricity_cost_zar', 'carbon_emissions_kg']].tail(10))

        # Display different graphs based on selection and role
        if operator_role == "Operator":
            if graph_type == "Temperature vs. Time":
                fig = px.line(filtered_data, x="timestamp", y="temperature", title="Temperature vs. Time")
                graph_placeholder.plotly_chart(fig)
            elif graph_type == "Pressure, Humidity & Vibration":
                fig = px.line(filtered_data, x="timestamp", y=["pressure", "humidity", "vibration"], 
                              title="Pressure, Humidity & Vibration vs. Time")
                graph_placeholder.plotly_chart(fig)
            # Other graphs as needed

        elif operator_role == "Technician":
            if graph_type == "Temperature vs. Time":
                fig = px.line(filtered_data, x="timestamp", y="temperature", title="Temperature vs. Time")
                graph_placeholder.plotly_chart(fig)
            # Detailed graphs relevant to maintenance work

        elif operator_role == "Supervisor":
            if graph_type == "Electricity Consumption & Cost":
                fig = px.line(filtered_data, x="timestamp", y=["electricity_consumption_kwh", "electricity_cost_zar"], 
                              title="Electricity Consumption & Cost")
                graph_placeholder.plotly_chart(fig)
            # Performance and decision-making graphs

        elif operator_role == "Manager":
            if graph_type == "Hourly Electricity Consumption & Cost":
                hourly_fig = px.bar(hourly_data_df[hourly_data_df["device_id"] == selected_machine], 
                                   x="hour", 
                                   y=["total_consumption_kwh", "total_cost_zar"],
                                   title="Hourly Electricity Consumption & Cost")
                graph_placeholder.plotly_chart(hourly_fig)

            elif graph_type == "Hourly Carbon Emissions & Cost":
                hourly_fig = px.bar(hourly_data_df[hourly_data_df["device_id"] == selected_machine], 
                                   x="hour", 
                                   y=["total_emissions_kg", "total_cost_zar"],
                                   title="Hourly Carbon Emissions & Cost")
                graph_placeholder.plotly_chart(hourly_fig)

            elif graph_type == "Pie Chart of Machine Temperatures":
                fig = px.pie(filtered_data, names="heat_treatment_process", values="temperature", 
                             title="Distribution of Machine Temperatures by Process")
                graph_placeholder.plotly_chart(fig)

            elif graph_type == "Bar Chart of Electricity Consumption and Costs":
                fig = px.bar(filtered_data, x="heat_treatment_process", y=["electricity_consumption_kwh", "electricity_cost_zar"], 
                             title="Electricity Consumption and Costs by Heat Treatment Process")
                graph_placeholder.plotly_chart(fig)

            elif graph_type == "Line Chart of Temperature Trends Over Time":
                fig = px.line(filtered_data, x="timestamp", y="temperature", 
                              title="Temperature Trends Over Time")
                graph_placeholder.plotly_chart(fig)

            elif graph_type == "Heatmap of Temperature Differences":
                fig = px.density_heatmap(filtered_data, x="timestamp", y="temperature", 
                                        title="Heatmap of Temperature Differences")
                graph_placeholder.plotly_chart(fig)

        time.sleep(5)  # Update every 2 seconds


if __name__ == "__main__":
    update_machine_data()
