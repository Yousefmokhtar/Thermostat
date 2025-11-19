#include <Arduino.h>
#include "../App_cfg.h"
#include "../Hal//GPIO/gpio.h"
#include "../Hal/SensorH/SensorH.h"
#include "ULS.h"

#if POT_DEBUG == STD_ON
#define DEBUG_PRINTLN(var) Serial.println(var)

#else
#define DEBUG_PRINTLN(var)

#endif

static void Ultrasonic_TriggerPulse(void)
{
    write_pin_Low(US_TRIG_PIN);
    delayMicroseconds(2);
    write_pin_high(US_TRIG_PIN);
    delayMicroseconds(10);
    write_pin_Low(US_TRIG_PIN);
}

void Ultrasonic_Init(void)
{
    GPIO_PinInit(US_TRIG_PIN, OUTPUT);
    GPIO_PinInit(US_ECHO_PIN, INPUT);
    write_pin_Low(US_TRIG_PIN);
}

float Ultrasonic_ReadDistanceCM(void)
{
    Ultrasonic_TriggerPulse();
    unsigned long duration = pulseIn(US_ECHO_PIN, HIGH, US_ECHO_TIMEOUT_US);

    if (duration == 0UL)
    {
        return -1.0f;
    }

    return (duration * SOUND_SPEED_CM_PER_US) / 2.0f;
}
