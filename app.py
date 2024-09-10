import streamlit as st
import requests
import pandas as pd

# Function to load data from the Flask API
@st.cache
def load_data():
    try:
        response = requests.get('http://localhost:5000/api/sensors')
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()
        return pd.DataFrame(data).T  # Convert JSON to DataFrame
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame

# Load and display data
df = load_data()
st.write(df)
