/*
 * robot-control_extender.cpp
 *
 *  Created on: Apr 24, 2024
 *      Author: Dustin Lehmann
 */

#include "robot-control_extender.h"

RobotControl_Extender::RobotControl_Extender() {

}

void RobotControl_Extender::init(extender_config_struct_t config) {

	this->config = config;

}

void RobotControl_Extender::start() {

}

void RobotControl_Extender::setStatusLED(int8_t status) {

	uint8_t data = (uint8_t) status;
	HAL_I2C_Mem_Write(this->config.hi2c,
	EXTENDER_ADDRESS, REG_ERROR_LED_CONFIG, 1, &data, 1, 100);
}

void RobotControl_Extender::rgbLED_intern_setState(uint8_t position,
		uint8_t state) {

	state = (state << 7) + 0;

	switch (position) {
	case 0:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_1_CONFIG, 1, &state, 1, 10);
		break;
	case 1:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_2_CONFIG, 1, &state, 1, 10);
		break;
	case 2:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_3_CONFIG, 1, &state, 1, 10);
		break;
	default:
		break;
	}
}

void RobotControl_Extender::rgbLED_intern_setColor(uint8_t position,
		uint8_t red, uint8_t green, uint8_t blue) {
	switch (position) {
	case 0:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_1_RED, 1, &red, 1, 10);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_1_GREEN, 1, &green, 1, 10);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_1_BLUE, 1, &blue, 1, 10);
		break;
	case 1:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_2_RED, 1, &red, 1, 10);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_2_GREEN, 1, &green, 1, 10);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_2_BLUE, 1, &blue, 1, 10);
		break;
	case 2:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_3_RED, 1, &red, 1, 10);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_3_GREEN, 1, &green, 1, 10);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_3_BLUE, 1, &blue, 1, 10);
		break;
	default:
		break;
	}
}

//void RobotControl_Extender::rgbLEDStrip_extern_setColor(uint8_t red,
//		uint8_t green, uint8_t blue) {
//
//	HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//	REG_EXTERNAL_RGB_GLOBAL_RED, 1, &red, 1, 10);
//	HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//	REG_EXTERNAL_RGB_GLOBAL_GREEN, 1, &green, 1, 10);
//	HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//	REG_EXTERNAL_RGB_GLOBAL_BLUE, 1, &blue, 1, 10);
//}


void RobotControl_Extender::rgbLEDStrip_extern_setColor(rgb_color_struct_t color) {

//	this->rgbLEDStrip_extern_setColor(color[0], color[1], color[2]);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_EXTERNAL_RGB_GLOBAL_RED, 1, &color.red, 1, 10);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_EXTERNAL_RGB_GLOBAL_GREEN, 1, &color.green, 1, 10);
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_EXTERNAL_RGB_GLOBAL_BLUE, 1, &color.blue, 1, 10);
}

void RobotControl_Extender::rgbLED_intern_blink(uint8_t position,
		uint16_t on_time_ms) {
	uint8_t time = (uint8_t)(on_time_ms / 10);
	uint8_t mode = 1;

	switch (position) {
	case 0:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_1_CONFIG, 1, &mode, 1, 10);

		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_1_BLINK_TIME, 1, &time, 1, 10);

		break;
	case 1:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_2_CONFIG, 1, &mode, 1, 10);

		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_2_BLINK_TIME, 1, &time, 1, 10);

		break;
	case 2:
		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_3_CONFIG, 1, &mode, 1, 10);

		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
		REG_STATUS_RGB_LED_3_BLINK_TIME, 1, &time, 1, 10);
		break;
	default:
		break;
	}
}

void RobotControl_Extender::buzzer_setConfig(float frequency, uint16_t on_time,
		uint8_t repeats) {

	uint8_t freq = (uint8_t)(frequency / 10);
	uint8_t time = (uint8_t)(on_time / 10);

	HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
	REG_BUZZER_FREQ, 1, &freq, 1, 10);

	HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
	REG_BUZZER_BLINK_TIME, 1, &time, 1, 10);

	HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
	REG_BUZZER_BLINK_COUNTER, 1, &repeats, 1, 10);

}
void RobotControl_Extender::buzzer_start() {
	uint8_t data = 1;
	HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
	REG_BUZZER_DATA, 1, &data, 1, 10);
}

//void RobotControl_Extender::setRGBLED_intern(uint8_t position, uint8_t red,
//		uint8_t green, uint8_t blue, int8_t state) {
//
//	uint8_t led_state = (uint8_t) state;
//
//	switch (position) {
//	case 0:
//
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_1_CONFIG, 1, &led_state, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_1_RED, 1, &red, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_1_GREEN, 1, &green, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_1_BLUE, 1, &blue, 1, 10);
//		break;
//	case 1:
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_2_CONFIG, 1, &led_state, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_2_RED, 1, &red, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_2_GREEN, 1, &green, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_2_BLUE, 1, &blue, 1, 10);
//		break;
//	case 2:
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_3_CONFIG, 1, &led_state, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_3_RED, 1, &red, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_3_GREEN, 1, &green, 1, 10);
//		HAL_I2C_Mem_Write(this->config.hi2c, EXTENDER_ADDRESS,
//				REG_STATUS_RGB_LED_3_BLUE, 1, &blue, 1, 10);
//		break;
//	default:
//		break;
//	}
//
//}

