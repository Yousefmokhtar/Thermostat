# NTI_Smart_Thermostat_System

# 🌡️ Thermostat System (ESP32)

A modular thermostat system built on ESP32 using a layered embedded architecture (APP → HAL → MCAL).  
The system reads 3 potentiometers to simulate **temperature**, **humidity**, and **target temperature**, then controls fan speed & heating based on automatic logic and publishes all data via **MQTT**.

---

## 📌 Features

- Reads Temperature, Humidity & Target Temp via POTs  
- Auto and Manual operation modes  
- Automatic fan-speed control (Low / Medium / High)  
- Heating ON/OFF with temperature deadband  
- MQTT publishing every 5 seconds  
- LED indicators for fan speed  
- Clean modular architecture (Thermostat, POT, LED, MQTT layers)

---


---

## 🛠️ Hardware Connections

### 🔘 Potentiometers
| Purpose         | Pin  |
|----------------|------|
| Temperature     | 34   |
| Humidity        | 35   |
| Target Temp     | 32   |

### 💡 LED Indicators
| Fan Speed | Pin |
|----------|-----|
| Low      | 25  |
| Medium   | 26  |
| High     | 27  |

---

## 🔧 System Logic Details

### 1️⃣ ADC → Temperature Mapping  
ADC: **0 → 4095** maps to **15°C → 35°C**

### 2️⃣ ADC → Humidity Mapping  
ADC: **0 → 4095** maps to **20% → 90%**

---

## 🧠 AUTO MODE Logic

Temperature difference:
temp_diff = target_temp – current_temp


### 🔥 If TOO COLD → Heating ON  
Fan speed decides based on how cold it is:

| Condition | Fan Speed |
|----------|-----------|
| temp_diff > 5°C  | HIGH   |
| temp_diff > 2°C  | MEDIUM |
| temp_diff > 0.5°C | LOW   |

### 🌡️ If TOO HOT → Heating OFF  
- Fan runs LOW for air circulation.

### 😊 If within ±0.5°C deadband →  
- Heating OFF  
- Fan OFF  

---

## 🧩 System Modes

| Mode | Description |
|------|-------------|
| OFF | Heater + Fan OFF |
| MANUAL | User sets fan speed manually |
| AUTO | Temperature logic manages everything |

---

## 📡 MQTT Topics

Published every **5 seconds**:

| Topic | Data |
|-------|------|
| `home/thermostat/temperature` | Current temperature |
| `home/thermostat/humidity` | Current humidity |
| `home/thermostat/target` | Target temperature |
| `home/thermostat/fanspeed` | 0=OFF, 1=LOW, 2=MED, 3=HIGH |
| `home/thermostat/heating` | 1=ON, 0=OFF |
| `home/thermostat/mode` | 0=OFF, 1=MANUAL, 2=AUTO |

---

## 🖥️ API Functions

```c
Initialization
Thermostat_Init();

Main loop
Thermostat_Process();

Set mode
Thermostat_SetMode(THERMOSTAT_MODE_AUTO);

Manual fan control
Thermostat_SetFanSpeed(FAN_SPEED_HIGH);

Set target temperature
Thermostat_SetTargetTemp(25.0f);
```
### 💡 LED Behavior

| Fan Speed | LED           |
| --------- | ------------- |
| LOW       | LED on pin 25 |
| MEDIUM    | LED on pin 26 |
| HIGH      | LED on pin 27 |
| OFF       | All LEDs OFF  |



### 🚀 Future Enhancements

Support real sensors (DHT22, SHT30)

Add OLED / E-paper display

Add WiFi configuration page

Add hysteresis per fan-speed

