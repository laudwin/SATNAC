import streamlit as st
import requests
import pandas as pd

st.title('Real-Time Sensor Dashboard')

@st.cache
def load_data():
    response = requests.get('http://localhost:5000/api/sensors')
    data = response.json()
    df = pd.DataFrame(data).T
    return df

df = load_data()
st.write(df)

st.line_chart(df[['temperature', 'pressure', 'humidity', 'vibration']])
