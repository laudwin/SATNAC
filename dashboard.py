import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
import json
import threading

# MQTT Configuration (Azure IoT Hub settings)
MQTT_BROKER = "temperature-simulation.azure-devices.net"
MQTT_PORT = 8883
MQTT_TOPIC = "devices/+/messages/events/#"  # Adjust topic as needed

# Data storage for real-time updates
machine_data = {}

# Dash App Setup
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Real-Time Machine Status Dashboard"),
    dcc.Dropdown(
        id='machine-dropdown',
        options=[{'label': f'Machine {i}', 'value': f'Machine-{i}'} for i in range(1, 6)],
        value='Machine-1'
    ),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    )
])

# MQTT Client Functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        machine_id = payload['device_id']
        machine_data[machine_id] = payload  # Store or update data
        print(f"Received data for {machine_id}: {payload}")  # Debug statement
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except KeyError as e:
        print(f"Missing expected key in data: {e}")

# Setup MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start MQTT Client in a separate thread
threading.Thread(target=mqtt_client.loop_forever).start()

@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('machine-dropdown', 'value')]
)
def update_graph_live(n, selected_machine):
    if selected_machine in machine_data:
        values = machine_data[selected_machine]
        trace = go.Scatter(
            x=[values['timestamp']],
            y=[values['temperature']],
            mode='lines+markers',
            name=f"{selected_machine} - {values['heat_treatment_process']}",
            text=[
                f"Temperature: {values['temperature']}°C<br>"
                f"Pressure: {values['pressure']} bar<br>"
                f"Humidity: {values['humidity']}%<br>"
                f"Vibration: {values['vibration']} m/s²<br>"
                f"Electricity Consumption: {values['electricity_consumption_kwh']} kWh<br>"
                f"Cost: R{values['electricity_cost_zar']}<br>"
                f"Evaluation: {values['consumption_evaluation']}"
            ]
        )
        layout = go.Layout(
            title=f"{selected_machine} Heat Treatment Process",
            xaxis={'title': 'Timestamp'},
            yaxis={'title': 'Temperature (°C)'},
            hovermode='closest'
        )
        return {'data': [trace], 'layout': layout}
    else:
        # Handle case where no data is available
        return {
            'data': [],
            'layout': go.Layout(
                title="No Data Available",
                xaxis={'title': 'Timestamp'},
                yaxis={'title': 'Temperature (°C)'}
            )
        }

if __name__ == '__main__':
    app.run_server(debug=True)
