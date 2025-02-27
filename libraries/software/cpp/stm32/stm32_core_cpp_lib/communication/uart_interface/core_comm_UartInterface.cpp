/*
 * serial_socket.cpp
 *
 *  Created on: 8 Jul 2022
 *      Author: Dustin Lehmann
 */

#include <communication/uart_interface/core_comm_UartInterface.h>

#if CORE_CONFIG_USE_UART && CORE_CONFIG_USE_RTOS

core_hardware_UART_config std_hardware_uart_config = { .mode =
		CORE_HARDWARE_UART_MODE_DMA, .cobs_encode_rx = 1, .cobs_encode_tx = 1,
		.queues = 1, };

core_comm_UartInterface_config_t std_uart_config = { .uart =
		std_hardware_uart_config, .use_protocol = 1, .use_queue = 1 };

/* ============================================================================= */
void core_comm_SerialSocket_RTOS_Task(void *SerialSocket) {
	UartInterface *socket = (UartInterface*) SerialSocket;

// Get the task handle and save it in the RTOS structure for later notifying this task
	socket->setTaskID(xTaskGetCurrentTaskHandle());

	while (!socket->exit) {

		// TODO: this is now waiting only for receiving a notification, but maybe we want to do other things
		uint32_t ulNotificationValue = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
		if (ulNotificationValue) {
			socket->rx_function();
		}

	}
	vTaskDelete(socket->getTaskID());
}

#endif
