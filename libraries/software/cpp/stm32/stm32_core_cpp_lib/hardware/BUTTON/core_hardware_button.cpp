/*
 * core_hardware_button.cpp
 *
 *  Created on: Jul 14, 2023
 *      Author: Dustin Lehmann
 */

#include "core_hardware_button.h"



core_hardware_Button::core_hardware_Button(GPIO_TypeDef* port, uint16_t pin) {
	this->port = port;
	this->pin = pin;
}


uint8_t core_hardware_Button::check() {
	return HAL_GPIO_ReadPin(this->port, this->pin);
}

