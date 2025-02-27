/*
 * serial_socket.h
 *
 *  Created on: Apr 6, 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_INC_CORE_UART_H_
#define CORE_INC_CORE_UART_H_

/* Source: https://programming.vip/docs/stm32-hal-library-learning-serial-idle-interrupt.html */

/* Prerequisites:
 *
 * enable UART RX and TX DMA Stream
 * add USER_UART_IRQHandler(&huart_x) to the corresponding UART IRQ Handler
 *
 */

#include "stm32h7xx_hal.h"
#include "stm32h7xx_hal_uart.h"
#include "stm32h7xx_hal_gpio.h"

#include "config_core.h"
#include "core_error.h"
#include "core_utils.h"

#define CORE_UART_RX_BUFFER_LENGTH 255
#define MAX_NUMBER_UART_SOCKETS 5
#define CORE_UART_USE_RX_QUEUE

#define CORE_UART_CALLBACK_RX 1
#define CORE_UART_CALLBACK_TX 2
#define CORE_UART_CALLBACK_RX_FULL 3

typedef enum {
	CORE_UART_STATE_NONE = 0,
	CORE_UART_STATE_INIT = 1,
	CORE_UART_STATE_ACTIVE = 2,
	CORE_UART_STATE_ERROR = 3
} core_hardware_Uart_State_t;

typedef struct core_uart_Init_t {
	UART_HandleTypeDef *huart;
	DMA_HandleTypeDef *hdma_rx;
	DMA_HandleTypeDef *hdma_tx;
	core_utils_BufferQueue_t *rx_queue;
	core_utils_BufferQueue_t *tx_queue;
	uint8_t rx_cobs_encode;
	uint8_t tx_cobs_encode;
} core_hardware_Uart_Init_t;

typedef struct core_uart_t {
	UART_HandleTypeDef *huart;
	DMA_HandleTypeDef *hdma_rx;
	DMA_HandleTypeDef *hdma_tx;
	core_hardware_Uart_State_t state;
	uint8_t rx_buf[CORE_UART_RX_BUFFER_LENGTH];
	uint8_t tx_buf[CORE_UART_RX_BUFFER_LENGTH];

	uint8_t encode_buf[256];
	uint8_t decode_buf[256];

	core_utils_BufferQueue_t *rx_queue;
	core_utils_BufferQueue_t *tx_queue;

	core_utils_Callback_t rx_callback;
	core_utils_Callback_t tx_callback;
	core_utils_Callback_t rx_full_callback;

	uint8_t rx_cobs_encode;
	uint8_t tx_cobs_encode;

	core_hardware_Uart_Init_t Init;

} core_hardware_Uart_t;

extern core_hardware_Uart_t *registered_uarts[MAX_NUMBER_UART_SOCKETS];

uint8_t core_hardware_Uart_Init(core_hardware_Uart_t *uart);
uint8_t core_hardware_Uart_Start(core_hardware_Uart_t *uart);
uint8_t core_hardware_Uart_Send(core_hardware_Uart_t *uart, uint8_t *data, uint8_t len);

uint8_t core_hardware_Uart_SendBlocking(core_hardware_Uart_t *uart, uint8_t *data, uint8_t len,
		uint16_t timeout);

uint8_t core_hardware_Uart_RegisterCallback(core_hardware_Uart_t *uart, uint8_t callback_id,
		void (*callback)(void *argument, void *params),
		void *params);

int8_t core_hardware_Uart_RxAvailable(core_hardware_Uart_t *uart);

uint8_t core_hardware_Uart_FlushTxBuffer(core_hardware_Uart_t *uart);

/* private functions */

void _core_hardware_Uart_SendNextBuffer(core_hardware_Uart_t *uart);

void _core_hardware_Uart_TxCpltCallback(UART_HandleTypeDef *huart);

void _core_hardware_Uart_RxFunction(core_hardware_Uart_t *uart, uint16_t size);

#endif /* CORE_INC_CORE_UART_H_ */
