/*
 * serial_socket.c
 *
 *  Created on: Apr 6, 2022
 *      Author: Dustin Lehmann
 */

#include <core_uart.h>

core_hardware_Uart_t *registered_uarts[MAX_NUMBER_UART_SOCKETS] = { NULL };
uint8_t num_registered_uarts = 0;

/*  */
uint8_t core_hardware_Uart_Init(core_hardware_Uart_t *uart) {

	if (uart->Init.huart == NULL) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_INIT);
	}
	if (uart->Init.hdma_rx == NULL) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_INIT);
	}
	if (uart->Init.hdma_tx == NULL) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_INIT);
	}

	if (num_registered_uarts == MAX_NUMBER_UART_SOCKETS) {
		uart->state = CORE_UART_STATE_ERROR;
		core_ErrorHandler(CORE_ERROR_HARDWARE_INIT);
	}
	if (uart->state != CORE_UART_STATE_NONE) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_INIT);
	}

	if (uart->Init.rx_queue == NULL || uart->Init.rx_queue->len == 0) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_INIT);
	}

	if (uart->Init.tx_queue == NULL || uart->Init.tx_queue->len == 0) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_INIT);
	}

	uart->huart = uart->Init.huart;
	uart->hdma_rx = uart->Init.hdma_rx;
	uart->hdma_tx = uart->Init.hdma_tx;
	uart->rx_queue = uart->Init.rx_queue;
	uart->tx_queue = uart->Init.tx_queue;

	uart->rx_cobs_encode = uart->Init.rx_cobs_encode;
	uart->tx_cobs_encode = uart->Init.tx_cobs_encode;

	registered_uarts[num_registered_uarts] = uart;
	num_registered_uarts++;
	uart->state = CORE_UART_STATE_INIT;
	return CORE_OK;
}

/*  */
uint8_t core_hardware_Uart_Start(core_hardware_Uart_t *uart) {
	if (uart->state == CORE_UART_STATE_NONE) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_INIT);
	}

	HAL_UARTEx_ReceiveToIdle_DMA(uart->huart, (uint8_t*) uart->rx_buf,
			CORE_UART_RX_BUFFER_LENGTH);
	uart->state = CORE_UART_STATE_ACTIVE;
	return CORE_OK;
}

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size) {
	for (int i = 0; i < MAX_NUMBER_UART_SOCKETS; i++) {
		if (!(registered_uarts[i] == NULL)
				&& (registered_uarts[i]->huart == huart)) {

			HAL_UARTEx_ReceiveToIdle_DMA(registered_uarts[i]->huart, (uint8_t*) registered_uarts[i]->rx_buf,
									CORE_UART_RX_BUFFER_LENGTH);
			_core_hardware_Uart_RxFunction(registered_uarts[i], Size);
		}
	}
}


void _core_hardware_Uart_RxFunction(core_hardware_Uart_t *uart, uint16_t size) {

	if (size == 0) {
		return;
	}

	if (uart->rx_cobs_encode) {
		uint8_t len_dec = cobsDecode(uart->rx_buf, size - 1,
				uart->decode_buf);
		core_utils_BufferQueue_WriteArray(uart->rx_queue, uart->decode_buf,
				len_dec);

	} else {
		core_utils_BufferQueue_WriteArray(uart->rx_queue, uart->rx_buf,
				size);
	}
	// Call the callback function for reception
	if (uart->rx_callback.registered) {
		uart->rx_callback.callback(NULL, uart->rx_callback.params);
	}

}

/*  */
uint8_t core_hardware_Uart_Send(core_hardware_Uart_t *uart, uint8_t *data,
		uint8_t len) {
	if (!(uart->state == CORE_UART_STATE_ACTIVE)) {
		return CORE_ERROR;
	}

	if (uart->tx_cobs_encode) {
		// Encode the data into the temporary encode buffer
		uint8_t len_enc = cobsEncode(data, len, uart->encode_buf);
		uart->encode_buf[len_enc] = 0x00; // Add the delimiter byte at the end
		core_utils_BufferQueue_WriteArray(uart->tx_queue, uart->encode_buf,
				len_enc + 1); // the length is is len_enc+1, since we added the delimiter byte at the end
	} else {
		// Add the data to the outgoing queue directly
		core_utils_BufferQueue_WriteArray(uart->tx_queue, data, len);
	}

	core_hardware_Uart_FlushTxBuffer(uart);
	return CORE_OK;
}

/** Send data over UART in blocking mode. This will only return as soon as the data is sent or the timeout occurs.
 @param *uart Pointer to UART
 @param *data Pointer to data buffer
 @param len Number of bytes to send
 @param timeout Number of milliseconds to wait for the data to be sent
 @return Success of sending
 */
uint8_t core_hardware_Uart_SendBlocking(core_hardware_Uart_t *uart,
		uint8_t *data, uint8_t len, uint16_t timeout) {
	if (!(uart->state == CORE_UART_STATE_ACTIVE)) {
		return CORE_ERROR;
	}
	uint8_t ret = HAL_UART_Transmit(uart->huart, data, len, timeout);

	return ret;
}

uint8_t core_hardware_Uart_FlushTxBuffer(core_hardware_Uart_t *uart) {
	// Check if the UART is busy
	if (uart->huart->gState == HAL_UART_STATE_READY) { //TODO: is this right or should I rather check if the tx queue has been worked off?
		_core_hardware_Uart_SendNextBuffer(uart);
		return CORE_OK;
	}
	return 0;
}

void _core_hardware_Uart_SendNextBuffer(core_hardware_Uart_t *uart) {
	// Check if there is a message pending in the tx buffer
	if (core_utils_BufferQueue_Available(uart->tx_queue) == 0) {
		return;
	}

	if (uart->huart->gState != HAL_UART_STATE_READY) {
		return;
	}

	uint8_t *buffer = NULL;
	uint8_t len = core_utils_BufferQueue_ReadPointer(uart->tx_queue, &buffer);
	HAL_UART_Transmit_DMA(uart->huart, buffer, len);
}

int8_t core_hardware_Uart_RxAvailable(core_hardware_Uart_t *uart) {
	return core_utils_BufferQueue_Available(uart->rx_queue);
}

uint8_t core_hardware_Uart_RegisterCallback(core_hardware_Uart_t *uart,
		uint8_t callback_id, void (*callback)(void *argument, void *params),
		void *params) {

	switch (callback_id) {
	case CORE_UART_CALLBACK_RX: {
		uart->rx_callback.callback = callback;
		uart->rx_callback.params = params;
		uart->rx_callback.registered = 1;
		break;
	}
	case CORE_UART_CALLBACK_TX: {
		uart->tx_callback.callback = callback;
		uart->tx_callback.params = params;
		uart->tx_callback.registered = 1;
		break;
	}
	}
	return CORE_OK;
}

/*  */


void _core_hardware_Uart_TxCpltCallback(UART_HandleTypeDef *huart) {
	for (int i = 0; i < num_registered_uarts; i++) {
		if (huart == registered_uarts[i]->huart) {
			_core_hardware_Uart_SendNextBuffer(registered_uarts[i]);

			if (registered_uarts[i]->tx_callback.registered) {
				registered_uarts[i]->tx_callback.callback(NULL,
						registered_uarts[i]->tx_callback.params);
			}
		}
	}
}

