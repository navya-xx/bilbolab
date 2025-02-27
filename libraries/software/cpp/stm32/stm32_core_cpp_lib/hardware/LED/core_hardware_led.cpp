/*
 * core_hardware_led.cpp
 *
 *  Created on: Jul 6, 2022
 *      Author: Dustin Lehmann
 */


#include "core_hardware_led.h"

core_hardware_LED::core_hardware_LED(GPIO_TypeDef* GPIOx, uint16_t PINx) {
	this->GPIOx = GPIOx;
	this->PINx = PINx;
}

void core_hardware_LED::on() {
	HAL_GPIO_WritePin(this->GPIOx, this->PINx, GPIO_PIN_SET);
}


void core_hardware_LED::off() {
	HAL_GPIO_WritePin(this->GPIOx, this->PINx, GPIO_PIN_RESET);
}

void core_hardware_LED::toggle() {
	HAL_GPIO_TogglePin(this->GPIOx, this->PINx);
}


