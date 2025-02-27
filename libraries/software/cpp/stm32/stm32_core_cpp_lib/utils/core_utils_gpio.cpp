/*
 * core_utils_gpio.cpp
 *
 *  Created on: Mar 15, 2023
 *      Author: lehmann_workstation
 */

#include "core_utils_gpio.h"

static core_utils_Callback<void, void> callbacks[16];
static void execute_gpio_callback(uint16_t gpio_pin);

core_utils_GPIO::core_utils_GPIO(GPIO_TypeDef *GPIOx, uint16_t pin) {
	this->GPIOx = GPIOx;
	this->pin = pin;
}

/* -------------------------------------------------------------------------------- */
void core_utils_GPIO::write(uint8_t value) {
	if (value) {
		HAL_GPIO_WritePin(GPIOx, pin, GPIO_PIN_SET);
	} else {
		HAL_GPIO_WritePin(GPIOx, pin, GPIO_PIN_RESET);
	}
}

/* -------------------------------------------------------------------------------- */
void core_utils_GPIO::toggle() {
	HAL_GPIO_TogglePin(GPIOx, pin);
}

/* -------------------------------------------------------------------------------- */
uint8_t core_utils_GPIO::read() {
	GPIO_PinState state = HAL_GPIO_ReadPin(GPIOx, pin);
	if (state == GPIO_PIN_SET) {
		return 1;
	} else {
		return 0;
	}
}

void core_utils_gpio_registerExtiCallback(uint16_t line,
		void (*function)(void)) {
	core_utils_gpio_registerExtiCallback(line,
			core_utils_Callback<void, void>(function));
}
/* -------------------------------------------------------------------------------- */
void core_utils_gpio_registerExtiCallback(uint16_t line,
		core_utils_Callback<void, void> callback) {
	switch (line) {
	case GPIO_PIN_0: {
		callbacks[0] = callback;
		break;
	}
	case GPIO_PIN_1: {
		callbacks[1] = callback;
		break;
	}
	case GPIO_PIN_2: {
		callbacks[2] = callback;
		break;
	}
	case GPIO_PIN_3: {
		callbacks[3] = callback;
		break;
	}
	case GPIO_PIN_4: {
		callbacks[4] = callback;
		break;
	}
	case GPIO_PIN_5: {
		callbacks[5] = callback;
		break;
	}
	case GPIO_PIN_6: {
		callbacks[6] = callback;
		break;
	}
	case GPIO_PIN_7: {
		callbacks[7] = callback;
		break;
	}
	case GPIO_PIN_8: {
		callbacks[8] = callback;
		break;
	}
	case GPIO_PIN_9: {
		callbacks[9] = callback;
		break;
	}
	case GPIO_PIN_10: {
		callbacks[10] = callback;
		break;
	}
	case GPIO_PIN_11: {
		callbacks[11] = callback;
		break;
	}
	case GPIO_PIN_12: {
		callbacks[12] = callback;
		break;
	}
	case GPIO_PIN_13: {
		callbacks[13] = callback;
		break;
	}
	case GPIO_PIN_14: {
		callbacks[14] = callback;
		break;
	}
	case GPIO_PIN_15: {
		callbacks[15] = callback;
		break;
	}
	}
}

/* -------------------------------------------------------------------------------- */
extern "C" {
void HAL_GPIO_EXTI_Callback(uint16_t gpio_pin) {
	execute_gpio_callback(gpio_pin);
}
}

static void execute_gpio_callback(uint16_t gpio_pin) {
	switch (gpio_pin) {
	case GPIO_PIN_0: {
		callbacks[0].call();
		break;
	}
	case GPIO_PIN_1: {
		callbacks[1].call();
		break;
	}
	case GPIO_PIN_2: {
		callbacks[2].call();
		break;
	}
	case GPIO_PIN_3: {
		callbacks[3].call();
		break;
	}
	case GPIO_PIN_4: {
		callbacks[4].call();
		break;
	}
	case GPIO_PIN_5: {
		callbacks[5].call();
		break;
	}
	case GPIO_PIN_6: {
		callbacks[6].call();
		break;
	}
	case GPIO_PIN_7: {
		callbacks[7].call();
		break;
	}
	case GPIO_PIN_8: {
		callbacks[8].call();
		break;
	}
	case GPIO_PIN_9: {
		callbacks[9].call();
		break;
	}
	case GPIO_PIN_10: {
		callbacks[10].call();
		break;
	}
	case GPIO_PIN_11: {
		callbacks[11].call();
		break;
	}
	case GPIO_PIN_12: {
		callbacks[12].call();
		break;
	}
	case GPIO_PIN_13: {
		callbacks[13].call();
		break;
	}
	case GPIO_PIN_14: {
		callbacks[14].call();
		break;
	}
	case GPIO_PIN_15: {
		callbacks[15].call();
		break;
	}
	}
}

