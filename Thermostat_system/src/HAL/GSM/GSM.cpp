#define TINY_GSM_MODEM_SIM800
#include <TinyGsmClient.h>
#include "GSM.h"


static TinyGsm* modem = nullptr;
static TinyGsmClient* client = nullptr;
static HardwareSerial* gsmSerial = nullptr;


void GSM_init(UARTN_t uart)
{
    // Initialize UART using your driver
    UART_init();

    // Get the serial port handler from your UART driver
    gsmSerial = UART_getSerial(uart);

    // Create TinyGSM modem object over this serial
    modem = new TinyGsm(*gsmSerial);

    // Create TCP client used for HTTP
    client = new TinyGsmClient(*modem);

    delay(3000);  // SIM800L needs time to boot

    // Restart the GSM module
    modem->restart();
}

GSM_Status_t GSM_connectNetwork(const char* apn, const char* user, const char* pass)
{
    if (!modem) return GSM_STATUS_ERROR;  // check modem initialized if null error

    Serial.println("Waiting for network...");
    if (!modem->waitForNetwork(60000)) {  // wait max 60s
        Serial.println("Network connection failed!");
        return GSM_STATUS_ERROR;
    }

    Serial.println("Connecting to GPRS...");
    if (!modem->gprsConnect(apn, user, pass)) {
        Serial.println("GPRS connection failed!");
        return GSM_STATUS_ERROR;
    }

    Serial.println("GPRS connected!");
    return GSM_STATUS_OK;
}


GSM_Status_t GSM_sendSMS(const char* number, const char* message)
{
    if (!modem) return GSM_STATUS_ERROR;  // Make sure modem is initialized

    Serial.println("Sending SMS to: " + String(number));

    if (modem->sendSMS(number, message)) {
        Serial.println("SMS sent successfully!");
        return GSM_STATUS_OK;
    } else {
        Serial.println("SMS sending failed!");
        return GSM_STATUS_ERROR;
    }
}


GSM_Status_t GSM_httpGET(const char* url, String& response)
{
    if (!modem || !client) return GSM_STATUS_ERROR;  // Ensure modem and client are ready

    // Convert URL to host and path
    String urlStr(url);
    String host, path;

    int slashIndex = urlStr.indexOf('/', 7); // skip "http://"
    if (slashIndex == -1) slashIndex = urlStr.length();

    host = urlStr.substring(7, slashIndex);        // host
    path = urlStr.substring(slashIndex);           // path

    Serial.println("Connecting to host: " + host);

    if (!client->connect(host.c_str(), 80)) {
        Serial.println("Connection failed");
        return GSM_STATUS_ERROR;
    }

    // Send HTTP GET request
    client->print("GET ");
    client->print(path);
    client->println(" HTTP/1.0");
    client->print("Host: ");
    client->println(host);
    client->println("Connection: close");
    client->println();

    // Read server response
    response = "";
    unsigned long timeout = millis();
    while (client->connected() && millis() - timeout < 10000) { // 10s timeout
        while (client->available()) {
            char c = client->read();
            response += c;
            timeout = millis();  // reset timeout after receiving data
        }
    }

    client->stop();  // close connection
    Serial.println("HTTP GET finished");

    return GSM_STATUS_OK;
}

GSM_Status_t GSM_httpPOST(const char* url, const char* data, String& response)
{
    if (!modem || !client) return GSM_STATUS_ERROR;

    // Convert URL to host and path
    String urlStr(url);
    String host, path;

    int slashIndex = urlStr.indexOf('/', 7); // skip "http://"
    if (slashIndex == -1) slashIndex = urlStr.length();

    host = urlStr.substring(7, slashIndex);   // host
    path = urlStr.substring(slashIndex);      // path

    Serial.println("Connecting to host: " + host);

    if (!client->connect(host.c_str(), 80)) {
        Serial.println("Connection failed");
        return GSM_STATUS_ERROR;
    }

    // Prepare POST request
    int contentLength = strlen(data);

    client->print("POST ");
    client->print(path);
    client->println(" HTTP/1.1");
    client->print("Host: ");
    client->println(host);
    client->println("Content-Type: application/x-www-form-urlencoded");
    client->print("Content-Length: ");
    client->println(contentLength);
    client->println("Connection: close");
    client->println();               // End of headers
    client->print(data);             // POST body

    // Read server response
    response = "";
    unsigned long timeout = millis();
    while (client->connected() && millis() - timeout < 10000) {
        while (client->available()) {
            char c = client->read();
            response += c;
            timeout = millis();  // reset timeout after receiving data
        }
    }

    client->stop();  // Close TCP connection
    Serial.println("HTTP POST finished");

    return GSM_STATUS_OK;
}


