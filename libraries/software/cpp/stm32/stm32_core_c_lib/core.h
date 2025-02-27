/*
 * core.h
 *
 *  Created on: 15 Apr 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_H_
#define CORE_H_

#include "config_board.h"
#include "core_board.h"
#include "core_uart.h"
#include "core_hardware.h"
#include "core_messages.h"
#include "core_comm_socket.h"
#include "core_utils.h"
#include "core_comm_messagehandler.h"

//#include "core_usb.h"


#define _RAM_D2 __attribute__(( section(".ramd2block") ))


typedef struct core_HardwareInit_CM4UART_t {
	UART_HandleTypeDef *huart;
	DMA_HandleTypeDef *hdma_rx;
	DMA_HandleTypeDef *hdma_tx;

} core_HardwareInit_CM4UART_t;

typedef struct core_HardwareInit_CM4SPI_t {
//	SPI_HandleTypeDef *hspi;
	DMA_HandleTypeDef *hdma_rx;
} core_HardwareInit_CM4SPI_t;

typedef struct core_HardwareInit_I2C_t {
	I2C_HandleTypeDef *hi2c_internal;
	I2C_HandleTypeDef *hi2c_external;
} core_HardwareInit_I2C_t;

typedef struct core_HardwareInit_t {

	core_HardwareInit_CM4UART_t cm4_uart;
	core_HardwareInit_CM4SPI_t cm4_spi;
	core_HardwareInit_I2C_t cm4_i2c;

} core_HardwareInit_t;

typedef struct core_t {

	core_comm_Socket_t *cm4_socket;

	core_HardwareInit_t HardwareInit;
} core_t;

uint8_t core_Init(core_t *core);

void core_RTOS_Start();
void core_RTOS_Task();

#endif /* CORE_H_ */
