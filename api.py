from flask import Flask, jsonify

app = Flask(__name__)

# Sample sensor data
data = {
    "Machine-1": {"temperature": 75.0, "pressure": 1.8, "humidity": 45, "vibration": 0.5},
    "Machine-2": {"temperature": 85.0, "pressure": 2.0, "humidity": 50, "vibration": 0.6},
    "Machine-3": {"temperature": 65.0, "pressure": 1.5, "humidity": 40, "vibration": 0.4}
}

@app.route('/api/sensors', methods=['GET'])
def get_sensor_data():
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
