#ifndef GSM_H
#define GSM_H

#include <Arduino.h>
#include "../UART/UART.h"

// Return type for functions
typedef enum {
    GSM_STATUS_OK = 0,
    GSM_STATUS_ERROR
} GSM_Status_t;

// Initialize GSM module
void GSM_init(UARTN_t uart);

// Connect to GPRS network
GSM_Status_t GSM_connectNetwork(const char* apn, const char* user, const char* pass);

// Send SMS message
GSM_Status_t GSM_sendSMS(const char* number, const char* message);

// GET HTTP request
GSM_Status_t GSM_httpGET(const char* url, String& response);

GSM_Status_t GSM_httpPOST(const char* url, const char* data, String& response);

#endif
