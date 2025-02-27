/*
 * led_driver.h
 *
 *  Created on: 9 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_HARDWARE_BOARD_HARDWARE_CORE_BOARD_LEDDRIVER_H_
#define CORE_HARDWARE_BOARD_HARDWARE_CORE_BOARD_LEDDRIVER_H_

#include "stm32h7xx_hal.h"

class core_board_LedDriver {
public:

	core_board_LedDriver(I2C_HandleTypeDef* hi2c, uint8_t address);

	void setStatusLed(uint8_t led_num, uint8_t red, uint8_t green, uint8_t blue);
	void setExternalLed(uint8_t led_num, uint8_t red, uint8_t green, uint8_t blue);
	void setBuzzer(uint16_t frequency, uint16_t time_ms);

	void sendCommand(uint8_t command, uint8_t *data, uint8_t len);
	I2C_HandleTypeDef* hi2c;
	const uint8_t address;
private:


};



#endif /* CORE_HARDWARE_BOARD_HARDWARE_CORE_BOARD_LEDDRIVER_H_ */
