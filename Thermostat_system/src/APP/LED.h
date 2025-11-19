#ifndef LED_H
#define LED_H
#include <stdint.h>

void LED_init(uint8_t LED_PIN);
void LED_ON(uint8_t LED_PIN);
void LED_OFF(uint8_t LED_PIN);
void LED_Toggle(uint8_t LED_PIN);
#endif