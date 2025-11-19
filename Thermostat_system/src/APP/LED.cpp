#include <Arduino.h>
#include "../App_cfg.h"
#include "../HAL/GPIO/gpio.h"
#include "LED.h"

#if POT_DEBUG == STD_ON
#define DEBUG_PRINTLN(var) Serial.println(var)
#else
#define DEBUG_PRINTLN(var)
#endif

void LED_init(uint8_t LED_PIN)
{
#if LED_ENABLED == STD_ON
    GPIO_PinInit(LED_PIN, GPIO_OUTPUT);
#endif
}
void LED_ON(uint8_t LED_PIN)
{
#if LED_ENABLED == STD_ON
    write_pin_high(LED_PIN);
#endif
}
void LED_OFF(uint8_t LED_PIN)
{
#if LED_ENABLED == STD_ON
    write_pin_Low(LED_PIN);
#endif
}
void LED_Toggle(uint8_t LED_PIN)
{
#if LED_ENABLED == STD_ON
    Toggle(LED_PIN);
#endif
}