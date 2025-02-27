/*
 * core_utils_gpio.h
 *
 *  Created on: 12 Mar 2023
 *      Author: Dustin Lehmann
 */

#ifndef UTILS_CORE_UTILS_GPIO_H_
#define UTILS_CORE_UTILS_GPIO_H_

#include "stm32h7xx.h"
#include "core_utils_Callback.h"

typedef enum core_utils_gpio_type_t {
	CORE_UTILS_GPIO_INPUT = 0, CORE_UTILS_GPIO_OUTPUT = 1,
} core_utils_gpio_type_t;

typedef enum core_utils_gpio_interrupt_id {

} core_utils_gpio_interrupt_id;


void core_utils_gpio_registerExtiCallback(uint16_t line, core_utils_Callback<void,void> callback);
void core_utils_gpio_registerExtiCallback(uint16_t line, void (* function) (void));


class core_utils_GPIO {
public:
	core_utils_GPIO(){

	}
	core_utils_GPIO(GPIO_TypeDef *GPIOx, uint16_t pin);
	void write(uint8_t value);
	void toggle();
	uint8_t read();

	void registerInterrupt(core_utils_gpio_interrupt_id callback_id,
			core_utils_Callback<void, void> callback);

	GPIO_TypeDef *GPIOx;
	uint16_t pin;
};

#endif /* UTILS_CORE_UTILS_GPIO_H_ */
