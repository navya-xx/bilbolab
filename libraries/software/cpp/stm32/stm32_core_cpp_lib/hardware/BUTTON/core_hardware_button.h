/*
 * core_hardware_button.h
 *
 *  Created on: Jul 14, 2023
 *      Author: Dustin Lehmann
 */

#ifndef HARDWARE_BUTTON_CORE_HARDWARE_BUTTON_H_
#define HARDWARE_BUTTON_CORE_HARDWARE_BUTTON_H_

#include "stm32h7xx.h"

class core_hardware_Button {
public:
	core_hardware_Button(GPIO_TypeDef* port, uint16_t pin);

	uint8_t check();


private:
	GPIO_TypeDef* port;
	uint16_t pin;
};


#endif /* HARDWARE_BUTTON_CORE_HARDWARE_BUTTON_H_ */
