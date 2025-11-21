from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_TEMP = "home/thermostat/temperature"
MQTT_TOPIC_HUMIDITY = "home/thermostat/humidity"
MQTT_TOPIC_TARGET = "home/thermostat/target"
MQTT_TOPIC_HEATING = "home/thermostat/heating"
MQTT_TOPIC_DISTANCE = "home/thermostat/distance"
MQTT_TOPIC_POT = "home/thermostat/pot"
MQTT_TOPIC_CONTROL = "home/thermostat/control"

data_cache = {
    "temperature": 0,
    "humidity": 0,
    "target_temp": 25,
    "heating_status": False,
    "distance": 0,
    "pot_value": 0,
    "last_update": "",
    "history": [],
    "mqtt_connected": False
}

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        data_cache["mqtt_connected"] = True
        
        client.subscribe(MQTT_TOPIC_TEMP)
        client.subscribe(MQTT_TOPIC_HUMIDITY)
        client.subscribe(MQTT_TOPIC_TARGET)
        client.subscribe(MQTT_TOPIC_HEATING)
        client.subscribe(MQTT_TOPIC_DISTANCE)
        client.subscribe(MQTT_TOPIC_POT)
        
        print(f"📡 Subscribed to topics:")
        print(f"   - {MQTT_TOPIC_TEMP}")
        print(f"   - {MQTT_TOPIC_HUMIDITY}")
        print(f"   - {MQTT_TOPIC_TARGET}")
        print(f"   - {MQTT_TOPIC_HEATING}")
        print(f"   - {MQTT_TOPIC_DISTANCE}")
        print(f"   - {MQTT_TOPIC_POT}")
    else:
        print(f"❌ Failed to connect to MQTT Broker. Return code: {rc}")
        data_cache["mqtt_connected"] = False

def on_disconnect(client, userdata, rc):
    print("⚠️  Disconnected from MQTT Broker")
    data_cache["mqtt_connected"] = False

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        
        if topic == MQTT_TOPIC_TEMP:
            data_cache["temperature"] = float(payload)
        elif topic == MQTT_TOPIC_HUMIDITY:
            data_cache["humidity"] = float(payload)
        elif topic == MQTT_TOPIC_TARGET:
            data_cache["target_temp"] = float(payload)
        elif topic == MQTT_TOPIC_HEATING:
            data_cache["heating_status"] = payload.lower() in ['true', '1', 'on']
        elif topic == MQTT_TOPIC_DISTANCE:
            data_cache["distance"] = int(payload)
        elif topic == MQTT_TOPIC_POT:
            data_cache["pot_value"] = float(payload)
        
        data_cache["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        history_entry = {
            "timestamp": data_cache["last_update"],
            "temperature": data_cache["temperature"],
            "humidity": data_cache["humidity"]
        }
        data_cache["history"].append(history_entry)
        
        if len(data_cache["history"]) > 100:
            data_cache["history"].pop(0)
            
        print(f"📊 {topic}: {payload}")
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def init_mqtt():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    
    try:
        print(f"🔌 Connecting to MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"❌ MQTT Connection Error: {e}")

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    return jsonify(data_cache)

@app.route('/api/set_target/<temp>')
def set_target(temp):
    try:
        temp = float(temp)
        data_cache["target_temp"] = temp
        mqtt_client.publish(MQTT_TOPIC_CONTROL, str(temp))
        mqtt_client.publish(MQTT_TOPIC_TARGET, str(temp))
        print(f"🎯 Published target temperature: {temp}°C to ESP32")
        return jsonify({"status": "success", "target": temp})
    except Exception as e:
        print(f"❌ Error publishing target: {e}")
        return jsonify({"status": "error", "message": str(e)})

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🏠 Cozy Thermostat - MQTT</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Quicksand', sans-serif;
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }
        
        body::before {
            content: "☁️";
            position: fixed;
            font-size: 80px;
            opacity: 0.3;
            top: 10%;
            left: 5%;
            animation: float 6s ease-in-out infinite;
        }
        
        body::after {
            content: "☁️";
            position: fixed;
            font-size: 60px;
            opacity: 0.3;
            top: 70%;
            right: 10%;
            animation: float 8s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }
        
        h1 {
            color: #ff6b6b;
            text-align: center;
            margin-bottom: 20px;
            font-size: 3em;
            text-shadow: 3px 3px 0px rgba(255, 255, 255, 0.8);
            font-weight: 700;
            animation: bounce 2s ease-in-out infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .mqtt-status {
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 20px;
            font-weight: 600;
        }
        
        .mqtt-connected {
            color: #4CAF50;
        }
        
        .mqtt-disconnected {
            color: #ff6b6b;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
            border-radius: 25px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.2);
            border: 3px solid #ffe0e0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: "";
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,107,107,0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .card:hover {
            transform: translateY(-8px) rotate(1deg);
            box-shadow: 0 12px 35px rgba(255, 107, 107, 0.3);
        }
        
        .card-title {
            font-size: 1em;
            color: #ff8787;
            margin-bottom: 15px;
            font-weight: 600;
            position: relative;
            z-index: 1;
        }
        
        .card-value {
            font-size: 3.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #ff6b6b 0%, #ffa07a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            position: relative;
            z-index: 1;
        }
        
        .card-unit {
            font-size: 1.8em;
            color: #ffb3b3;
            margin-left: 5px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            margin-right: 10px;
            animation: glow 2s ease-in-out infinite;
        }
        
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 5px currentColor; }
            50% { box-shadow: 0 0 20px currentColor; }
        }
        
        .status-on {
            background: #ff6b6b;
            color: #ff6b6b;
        }
        
        .status-off {
            background: #ffd6d6;
            color: #ffd6d6;
            animation: none;
        }
        
        .control-section {
            background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
            border-radius: 30px;
            padding: 40px;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.2);
            border: 3px solid #ffe0e0;
        }
        
        .control-section h2 {
            color: #ff6b6b;
            font-weight: 700;
            margin-bottom: 25px;
        }
        
        .slider-container {
            margin: 25px 0;
            background: #fff;
            padding: 25px;
            border-radius: 20px;
            box-shadow: inset 0 2px 10px rgba(255, 107, 107, 0.1);
        }
        
        .slider-container label {
            color: #ff8787;
            font-weight: 600;
            font-size: 1.1em;
        }
        
        .slider {
            width: 100%;
            height: 12px;
            border-radius: 10px;
            background: linear-gradient(90deg, #ffd6d6 0%, #ff6b6b 100%);
            outline: none;
            -webkit-appearance: none;
            margin-top: 15px;
        }
        
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #ff6b6b;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.5);
            border: 3px solid white;
            transition: all 0.3s ease;
        }
        
        .slider::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 6px 20px rgba(255, 107, 107, 0.7);
        }
        
        .slider::-moz-range-thumb {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #ff6b6b;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.5);
            border: 3px solid white;
        }
        
        .info-box {
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.1);
        }
        
        .info-box p {
            color: #ff8787;
            margin: 8px 0;
            font-weight: 600;
        }
        
        .info-box span {
            color: #ff6b6b;
            font-weight: 700;
            font-size: 1.1em;
        }
        
        .chart-container {
            background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
            border-radius: 30px;
            padding: 40px;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.2);
            border: 3px solid #ffe0e0;
            margin-top: 30px;
        }
        
        .chart-container h2 {
            color: #ff6b6b;
            font-weight: 700;
            margin-bottom: 25px;
        }
        
        canvas {
            max-width: 100%;
        }
        
        .last-update {
            text-align: center;
            color: #ff6b6b;
            margin-top: 25px;
            font-size: 1em;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.7);
            padding: 15px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <h1>🏠  Thermostat - MQTT 🌡️</h1>
        
        <div class="mqtt-status">
            <span id="mqtt-status" class="mqtt-disconnected">🔴 MQTT Disconnected</span>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">🌡️ Temperature</div>
                <div>
                    <span class="card-value" id="temperature">--</span>
                    <span class="card-unit">°C</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">💧 Humidity</div>
                <div>
                    <span class="card-value" id="humidity">--</span>
                    <span class="card-unit">%</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">🎯 Target Temp</div>
                <div>
                    <span class="card-value" id="target">--</span>
                    <span class="card-unit">°C</span>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">🔥 Heating</div>
                <div>
                    <span class="status-indicator" id="heating-indicator"></span>
                    <span class="card-value" id="heating-status" style="font-size: 2em;">--</span>
                </div>
            </div>
        </div>
        
        <div class="control-section">
            <h2>🎛️ Temperature Control</h2>
            <div class="slider-container">
                <label>Set Target: <span id="slider-value">25</span>°C 🌡️</label>
                <input type="range" min="15" max="35" value="25" class="slider" id="temp-slider">
            </div>
            <div class="info-box">
                <p>📏 Distance: <span id="distance">--</span> cm</p>
                <p>🎚️ Potentiometer: <span id="pot">--</span></p>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📊 Temperature History</h2>
            <canvas id="tempChart"></canvas>
        </div>
        
        <div class="last-update">
            💝 Last Update: <span id="last-update">--</span>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('tempChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '🌡️ Temperature (°C)',
                    data: [],
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.2)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 5,
                    pointBackgroundColor: '#ff6b6b',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }, {
                    label: '💧 Humidity (%)',
                    data: [],
                    borderColor: '#ffa07a',
                    backgroundColor: 'rgba(255, 160, 122, 0.2)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3,
                    pointRadius: 5,
                    pointBackgroundColor: '#ffa07a',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#ff6b6b',
                            font: {
                                size: 14,
                                weight: 'bold',
                                family: 'Quicksand'
                            },
                            padding: 15
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            color: '#ff8787',
                            font: {
                                family: 'Quicksand',
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(255, 107, 107, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#ff8787',
                            font: {
                                family: 'Quicksand',
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(255, 107, 107, 0.1)'
                        }
                    }
                }
            }
        });
        
        function updateDashboard() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temperature').textContent = data.temperature.toFixed(1);
                    document.getElementById('humidity').textContent = data.humidity.toFixed(0);
                    document.getElementById('target').textContent = data.target_temp.toFixed(1);
                    document.getElementById('distance').textContent = data.distance;
                    document.getElementById('pot').textContent = data.pot_value.toFixed(1);
                    document.getElementById('last-update').textContent = data.last_update;
                    
                    const mqttStatus = document.getElementById('mqtt-status');
                    if (data.mqtt_connected) {
                        mqttStatus.textContent = '🟢 MQTT Connected';
                        mqttStatus.className = 'mqtt-connected';
                    } else {
                        mqttStatus.textContent = '🔴 MQTT Disconnected';
                        mqttStatus.className = 'mqtt-disconnected';
                    }
                    
                    const heatingStatus = data.heating_status ? 'ON' : 'OFF';
                    document.getElementById('heating-status').textContent = heatingStatus;
                    
                    const indicator = document.getElementById('heating-indicator');
                    if (data.heating_status) {
                        indicator.className = 'status-indicator status-on';
                    } else {
                        indicator.className = 'status-indicator status-off';
                    }
                    
                    if (data.history.length > 0) {
                        const labels = data.history.map(h => h.timestamp.split(' ')[1]);
                        const temps = data.history.map(h => h.temperature);
                        const humidity = data.history.map(h => h.humidity);
                        
                        chart.data.labels = labels;
                        chart.data.datasets[0].data = temps;
                        chart.data.datasets[1].data = humidity;
                        chart.update();
                    }
                })
                .catch(error => console.error('Error:', error));
        }
        
        const slider = document.getElementById('temp-slider');
        const sliderValue = document.getElementById('slider-value');
        
        slider.addEventListener('input', function() {
            sliderValue.textContent = this.value;
            document.getElementById('target').textContent = parseFloat(this.value).toFixed(1);
        });
        
        slider.addEventListener('change', function() {
            const newTarget = parseFloat(this.value);
            
            fetch('/api/set_target/' + newTarget)
                .then(response => response.json())
                .then(data => {
                    console.log('✅ Target set:', data);
                })
                .catch(error => console.error('❌ Error:', error));
        });
        
        updateDashboard();
        setInterval(updateDashboard, 1000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    with open('templates/dashboard.html', 'w') as f:
        f.write(HTML_TEMPLATE)
    
    print("=" * 70)
    print("🏠 SMART THERMOSTAT DASHBOARD - MQTT VERSION")
    print("=" * 70)
    print()
    init_mqtt()
    print()
    print("🌐 Dashboard starting on: http://localhost:5000")
    print("📡 Listening for MQTT messages...")
    print()
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
