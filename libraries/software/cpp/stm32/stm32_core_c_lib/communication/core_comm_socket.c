/*
 * communication.c
 *
 *  Created on: Apr 5, 2022
 *      Author: Dustin Lehmann
 */

#include <core_comm_socket.h>

core_comm_Socket_t *core_comm_socket_registered_sockets[2] = { 0 };
uint8_t num_registered_sockets = 0;

/* ======================================================================================== */

uint8_t core_comm_Socket_Init(core_comm_Socket_t *socket) {

	if (socket->state != CORE_COMM_SOCKET_STATE_NONE) {
		core_ErrorHandler(0);
	}

	if (socket->Init.uart == NULL) {
		core_ErrorHandler(0);
	}

	if (socket->Init.tx_msg_queue == NULL) {
		core_ErrorHandler(0);
	}

	if (socket->Init.rx_msg_queue == NULL) {
		core_ErrorHandler(0);
	}

	socket->uart = socket->Init.uart;
	socket->interface = socket->Init.interface;
	socket->tx_msg_queue = socket->Init.tx_msg_queue;
	socket->rx_msg_queue = socket->Init.rx_msg_queue;

	socket->rx_msg_queue_robot = NULL;

	if (socket->uart->state == CORE_UART_STATE_NONE) {
		core_hardware_Uart_Init(socket->uart);
	}

	if (socket->uart->state != CORE_UART_STATE_INIT) {
		core_ErrorHandler(0);
	}

#ifdef CORE_COMM_SOCKET_RTOS
	core_hardware_Uart_RegisterCallback(socket->uart, CORE_UART_CALLBACK_RX,
			_core_comm_Socket_RTOS_RxNotify_CB, socket);
#else
	core_hardware_Uart_RegisterCallback(socket->uart, CORE_UART_CALLBACK_TX,
			_core_comm_Socket_TxCpltCallback, socket->uart);
#endif

	core_comm_socket_registered_sockets[num_registered_sockets] = socket;
	num_registered_sockets++;

	socket->state = CORE_COMM_SOCKET_STATE_INIT;

	return CORE_OK;
}

/* ======================================================================================== */

uint8_t core_comm_Socket_Start(core_comm_Socket_t *socket) {
	if (socket->state != CORE_COMM_SOCKET_STATE_INIT) {
		core_ErrorHandler(0);
	}

	uint8_t ret = core_hardware_Uart_Start(socket->uart);

	if (ret == CORE_OK) {
		socket->state = CORE_COMM_SOCKET_STATE_ACTIVE;
	}
	return ret;
}

/* ======================================================================================== */

uint8_t core_comm_Socket_Send(core_comm_Socket_t *socket, uint8_t *data,
		uint8_t len) {

	uint8_t ret = core_hardware_Uart_Send(socket->uart, data, len);

	return ret;
}

/* ======================================================================================== */

/*	core_comm_Socket_SendMessage
 *	- Sends a message object over the serial socket.
 *	- the message is encoded and handed over the corresponding UART
 */
uint8_t core_comm_Socket_SendMessage(core_comm_Socket_t *socket,
		core_comm_Message_t *msg) {

	uint8_t len = core_comm_Message_Encode(msg, socket->tx_buf);
	uint8_t ret = core_hardware_Uart_Send(socket->uart, socket->tx_buf, len);

	return ret;
}

/* ======================================================================================== */

/*	core_comm_Socket_SendMessageBlocking
 *	- Sends a message in a blocking way over the serial socket
 *	- the message object is encoded and handed over to the blocking sending function of the corresponding UART
 */
uint8_t core_comm_Socket_SendMessageBlocking(core_comm_Socket_t *socket,
		core_comm_Message_t *msg, uint16_t timeout) {


	uint8_t len = core_comm_Message_Encode(msg, socket->tx_buf);
	uint8_t ret = core_hardware_Uart_SendBlocking(socket->uart, socket->tx_buf,
			len, timeout);
	return ret;
}

/* ======================================================================================== */

/*	core_comm_Socket_PollRxBuffer
 *
 *
 *
 */
uint8_t core_comm_Socket_RxFunction(core_comm_Socket_t *socket) {
	uint8_t num_messages = 0;
	// Check if there are messages in the rx buffer of the UART
	while (core_hardware_Uart_RxAvailable(socket->uart) > 0) {

		// Get the pointer to the next message in the UART Rx Queue
		uint8_t *msg_buffer = NULL;
		uint8_t len = core_utils_BufferQueue_ReadPointer(socket->uart->rx_queue,
				&msg_buffer);

		// Check if the buffer contains a valid message
		uint8_t message_ok = core_comm_Message_Check(msg_buffer, len);

		// If the message is faulty, skip to the next message and reduce the overall message count
		if (message_ok == CORE_ERROR) {
			continue;
		}

		// Parse the message from the UART Rx Queue into a temporary message _rxMsg
		uint8_t success = core_comm_Message_Decode(msg_buffer, len,
				&socket->_rxMsg);

		if (success) {

			// Increment the message counter to return at the end of the function
			num_messages++;

			// Check the first address byte to determine the queue to write the message into
			uint8_t add1 = socket->_rxMsg.address_1;

			if (add1 == 0) {  // Core firmware address

				// Write the temporary message into the core rx_msg_queue
				core_comm_MsgQueue_Write(socket->rx_msg_queue, &socket->_rxMsg);

				// If the callback for rx_msg is registered, call it here
				if (socket->callbacks.rx_msg.registered) {
					socket->callbacks.rx_msg.callback(
							&socket->rx_msg_queue->messages[socket->rx_msg_queue->idx_write
									- 1], socket->callbacks.rx_msg.params);
				}
			} else {
				// Check if the robot message queue has been set
				if (socket->rx_msg_queue_robot != NULL) {
					core_comm_MsgQueue_Write(socket->rx_msg_queue_robot,
							&socket->_rxMsg);

					// If the callback for the robot layer (add_1 \neq 0) is registered, call it here
					if (socket->callbacks.rx_msg_robot.registered) {
						socket->callbacks.rx_msg_robot.callback(
								&socket->rx_msg_queue_robot->messages[socket->rx_msg_queue_robot->idx_write
										- 1],
								socket->callbacks.rx_msg_robot.params);
					}

				} else { // Incorporate it into the main message queue
					// TODO
				}
			}

		} else { // Decoding was unsuccessful
			continue;
		}
	}
	return num_messages;
}

/* ======================================================================================== */
uint8_t core_comm_Socket_RegisterCallback(core_comm_Socket_t *socket,
		core_comm_socket_CallbackID_t callback_id,
		void (*callback)(void *argument, void *params), void *params) {

	switch (callback_id) {
	case CORE_COMM_SOCKET_CB_RX_MSG: {
		socket->callbacks.rx_msg.params = params;
		socket->callbacks.rx_msg.callback = callback;
		socket->callbacks.rx_msg.registered = 1;
		break;
	}
	case CORE_COMM_SOCKET_CB_RX_MSG_ROBOT: {
		socket->callbacks.rx_msg_robot.params = params;
		socket->callbacks.rx_msg_robot.callback = callback;
		socket->callbacks.rx_msg_robot.registered = 1;
		break;
	}
	default: {
		return CORE_ERROR;
		break;
	}
	}
	return CORE_OK;
}

/* ======================================================================================== */
/* RTOS Function */

void core_comm_Socket_RTOS_Start(core_comm_Socket_t *socket) {
	if (socket->state != CORE_COMM_SOCKET_STATE_INIT) {
		core_ErrorHandler(0);
	}

	const osThreadAttr_t rx_task_attributes = { .name = "socket_rx_task",
			.stack_size = CORE_COMM_SOCKET_RTOS_RX_STACKSIZE, .priority =
					(osPriority_t) CORE_COMM_SOCKET_RTOS_RX_PRIORITY };

	socket->RTOS.rx_task_handle = osThreadNew(core_comm_Socket_RTOS_RxTask,
			socket, &rx_task_attributes);

	uint8_t ret = core_hardware_Uart_Start(socket->uart);

	if (ret == CORE_OK) {
		socket->state = CORE_COMM_SOCKET_STATE_ACTIVE;
	}
}

void core_comm_Socket_RTOS_RxTask(void *argument) {

	core_comm_Socket_t *socket = (core_comm_Socket_t*) argument;

	while (1) {
		// Wait until the task is notified
		uint32_t ulNotificationValue = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
		if (ulNotificationValue) {
			core_comm_Socket_RxFunction(socket);
		}
	}
}

/* This function is hooked in as a Callback into the UART RX IDLE Interrupt. It sends a notification to the rx task to handle the incoming message */
void _core_comm_Socket_RTOS_RxNotify_CB(void *argument, void *_socket) {
	core_comm_Socket_t *socket = (core_comm_Socket_t*) _socket;
	if (socket->RTOS.rx_task_handle) {

		BaseType_t xHigherPriorityTaskWoken = pdFALSE;
		vTaskNotifyGiveFromISR(socket->RTOS.rx_task_handle,
				&xHigherPriorityTaskWoken);
		portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
	}
}

/* ======================================================================================== */

void _core_comm_Socket_TxCpltCallback(void *argument, void *params) {
	core_hardware_Uart_t *uart = (core_hardware_Uart_t*) params;
	for (int i = 0; i < num_registered_sockets; i++) {
		if (core_comm_socket_registered_sockets[i]->uart == uart) {
			nop();
		}
	}
}

/* ======================================================================================== */
/* This function is called when the UART receives a message */
void _core_comm_Socket_RxCpltCallback(void *argument, void *_uart) {
	core_hardware_Uart_t *uart = (core_hardware_Uart_t*) _uart;
	for (int i = 0; i < num_registered_sockets; i++) {
		if (core_comm_socket_registered_sockets[i]->uart == uart) {
			nop();
		}
	}
}

/* ======================================================================================== */

/* This function flushes the next message into the UART */
void _core_comm_Socket_SendNextMessage(core_comm_Socket_t *socket) {
	if (core_comm_MsgQueue_Available(socket->tx_msg_queue) > 0) {
		uint8_t len = core_comm_Message_Encode(
				core_comm_MsgQueue_ReadPointer(socket->tx_msg_queue),
				socket->tx_buf);

		core_hardware_Uart_Send(socket->uart, socket->tx_buf, len);
	}
}

