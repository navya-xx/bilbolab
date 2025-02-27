/*
 * board.h
 *
 *  Created on: 7 Apr 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_INC_CORE_BOARD_H_
#define CORE_INC_CORE_BOARD_H_

#include <config_board.h>
#include "stm32h7xx_hal.h"

//typedef struct {
//	SPI_TypeDef* imu_spi;
//} core_board_interfaces_t;


extern uint8_t core_board_initialized;

uint8_t core_Board_Init();

uint8_t core_Board_Check();

uint8_t core_Board_CheckCM4();

float core_Board_ReadInputVoltage();
uint8_t core_Board_ReadUSBVoltage();

uint8_t core_Board_GetHardwareRevision();
uint8_t core_Board_GetFirmwareRevision();

void core_Board_SetLed(uint8_t led_num, int8_t state);

uint8_t core_Board_CheckLedDriver();
uint8_t core_Board_CheckMemory();

typedef enum {
	STATUS_LED_OFF = 0,
	STATUS_LED_OK = 1,
	STATUS_LED_WARNING = 2,
	STATUS_LED_ERROR = 3,
	STATUS_LED_CONNECTED = 4
} core_status_led_state_t;

void core_Board_SetStatusLedColor(uint8_t led, uint8_t red, uint8_t green,
		uint8_t blue);
void core_Board_SetStatusLedState(uint8_t led, core_status_led_state_t state);
void core_Board_SetStatusLedBlinking(uint8_t led, uint8_t freq);

void core_Board_SetBuzzer(uint16_t freq, uint16_t msec);

void core_Board_SetExternalPower(uint8_t state);
uint8_t core_Board_GetExternalPowerState();

#endif /* CORE_INC_CORE_BOARD_H_ */
