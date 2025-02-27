/*
 * board.c
 *
 *  Created on: 7 Apr 2022
 *      Author: Dustin Lehmann
 */

#include <core_board.h>

uint8_t core_board_initialized = 0;

uint8_t core_Board_Init() {

	/* Disable External Power */
	core_Board_SetExternalPower(0);

	/* Disable LED */
	core_Board_SetLed(1, 0);

	core_board_initialized = 1;
	return 1;
}

uint8_t core_Board_CheckCM4() {

	/* Read the PG Pin. If PG is high, the PMIC of the CM4 is running. */
	uint8_t ret = HAL_GPIO_ReadPin(CORE_BOARD_GPIO_CM4_PG_PORT,
	CORE_BOARD_GPIO_CM4_PG_PIN);
	return ret;
}

float core_Board_ReadInputVoltage() {

	return 0;
}

uint8_t core_Board_ReadUSBVoltage() {
	uint8_t ret = HAL_GPIO_ReadPin(CORE_BOARD_GPIO_USB_DETECT_PORT,
	CORE_BOARD_GPIO_USB_DETECT_PIN);
	return ret;
}

void core_Board_SetLed(uint8_t led_num, int8_t state) {
	if (led_num == 1) {
		if (state == 0 || state == 1) {
			HAL_GPIO_WritePin(CORE_BOARD_LED_1_PORT,
			CORE_BOARD_LED_1_PIN, state);
		} else if (state == -1) {
			HAL_GPIO_TogglePin(CORE_BOARD_LED_1_PORT,
			CORE_BOARD_LED_1_PIN);
		}
	} else if (led_num == 2) {
		if (state == 0 || state == 1) {
			HAL_GPIO_WritePin(CORE_BOARD_LED_2_PORT,
			CORE_BOARD_LED_2_PIN, state);
		} else if (state == -1) {
			HAL_GPIO_TogglePin(CORE_BOARD_LED_2_PORT,
			CORE_BOARD_LED_2_PIN);
		}
	}

#ifdef CORE_BOARD_REV_2
// TODO
#endif
}

void core_Board_SetExternalPower(uint8_t state) {
	HAL_GPIO_WritePin(CORE_BOARD_GPIO_POWER_OUT_SWITCH_PORT,
	CORE_BOARD_GPIO_POWER_OUT_SWITCH_PIN, state);
}

uint8_t core_Board_GetExternalPowerState() {
	return ((CORE_BOARD_GPIO_POWER_OUT_SWITCH_PORT->ODR)
			& CORE_BOARD_GPIO_POWER_OUT_SWITCH_PIN) > 0;
}
