/*
 * led_driver.cpp
 *
 *  Created on: 9 Jul 2022
 *      Author: Dustin Lehmann
 */

#include "core_board_LedDriver.h"


/* ============================================================================= */
core_board_LedDriver::core_board_LedDriver(I2C_HandleTypeDef *hi2c,
		uint8_t address): address(address) {
	this->hi2c = hi2c;
}

/* ============================================================================= */
void core_board_LedDriver::setStatusLed(uint8_t led_num, uint8_t red,
		uint8_t green, uint8_t blue) {

}

/* ============================================================================= */
void core_board_LedDriver::setExternalLed(uint8_t led_num, uint8_t red,
		uint8_t green, uint8_t blue) {

}

/* ============================================================================= */
void core_board_LedDriver::setBuzzer(uint16_t frequency, uint16_t time_ms) {

}

/* ============================================================================= */
void core_board_LedDriver::sendCommand(uint8_t command, uint8_t *data, uint8_t len) {
	// TODO: Consider this to make it DMA or IT


}
