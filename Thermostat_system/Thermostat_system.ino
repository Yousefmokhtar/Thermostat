#include <Arduino.h>
#include "src/HAL/MQTT/MQTT.h"
#include "src/HAL/WIFI/wifi.h"
#include "src/HAL/GSM/SIM2.h"
#include "src/APP/Thermostat/Thermostat.h"
#include "src/App_cfg.h"

bool thermostatInitialized = false;



void setup()  
{
    Serial.begin(9600);
    delay(1000);
    
    Serial.println("\n=== Smart Thermostat System ===");
    Serial.println("Initializing...");

    // Configure WiFi
    WIFI_Config_t g_wifiCfg_cpy = {
        .ssid = SSID,
        .password = PASSWORD,
        .reconnect_interval_ms = 5000,
        .on_connect = onWifiConnected,
        .on_disconnect = onWifiDisconnected
    };

    // Initialize WiFi
    WIFI_Init_(&g_wifiCfg_cpy);
    
    Serial.println("WiFi initialization started");
    
    // Wait a bit for WiFi to start connecting
    delay(2000);
    
    // Initialize GSIM 
    SIM_MODULE_Init();
    
    // Initialize thermostat hardware (LEDs, ADC pins)
    Thermostat_Init();
    thermostatInitialized = true;
    
    Serial.println("Thermostat hardware initialized");
    Serial.println("System ready!");


}

void loop() 
{
    // Process WiFi status (handles auto-reconnection)
    WIFI_Process();

    // Only run MQTT and thermostat logic if WiFi is connected
    if (WIFI_IsConnected() && mqttInitialized) 
    {
        // Run MQTT loop
        MQTT_Loop();
        
        // Process thermostat (read sensors, control logic, LED updates)
        if (thermostatInitialized)
        {
            Thermostat_Process();
        }
    }
    
    // Print status periodically for debugging
    static unsigned long lastStatus = 0;
    if (millis() - lastStatus > 10000) // Every 10 seconds
    {
        Serial.println("\n--- System Status ---");
        Serial.print("WiFi: ");
        Serial.println(WIFI_IsConnected() ? "Connected" : "Disconnected");
        Serial.print("MQTT: ");
        Serial.println(MQTT_IsConnected() ? "Connected" : "Disconnected");
        
        if (thermostatInitialized)
        {
            Thermostat_Status_t status = Thermostat_GetStatus();
            Serial.print("Temp: ");
            Serial.print(status.temperature, 1);
            Serial.print("°C | Target: ");
            Serial.print(status.target_temp, 1);
            Serial.print("°C | Humidity: ");
            Serial.print(status.humidity, 1);
            Serial.print("% | Fan: ");
            Serial.print(status.fan_speed);
            Serial.print(" | Heating: ");
            Serial.println(status.heating ? "ON" : "OFF");
        }
        
        lastStatus = millis();
    }
    
    // Small delay to prevent watchdog issues
    delay(10);
}