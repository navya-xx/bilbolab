/*
 * serial_socket.h
 *
 *  Created on: 8 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_COMMUNICATION_SERIAL_SOCKET_H_
#define CORE_COMMUNICATION_SERIAL_SOCKET_H_

#include "core_comm_MessageQueue.h"
#include "core_comm_SerialProtocol.h"
#include "core_includes.h"
#include "core_hardware_UART.h"

#if CORE_CONFIG_USE_UART && CORE_CONFIG_USE_RTOS

#define CORE_COMM_SERIAL_SOCKET_RTOS_RX_STACKSIZE 1028*4
#define CORE_COMM_SERIAL_SOCKET_RTOS_RX_PRIORITY osPriorityAboveNormal3

/* ---------------------------------------------------------- */
typedef enum core_comm_UartInterface_callback_id_t {
	CORE_COMM_SERIAL_SOCKET_CB_RX,
	CORE_COMM_SERIAL_SOCKET_CB_RX_MSG,
	CORE_COMM_SERIAL_SOCKET_CB_ERROR
} core_comm_UartInterface_callback_id_t;

/* ---------------------------------------------------------- */
typedef enum core_comm_UartInterface_status_t {
	CORE_COMM_SERIAL_SOCKET_STATE_NONE,
	CORE_COMM_SERIAL_SOCKET_STATE_INIT,
	CORE_COMM_SERIAL_SOCKET_STATE_RUN,
	CORE_COMM_SERIAL_SOCKET_STATE_ERROR
} core_comm_UartInterface_status_t;

/* ---------------------------------------------------------- */
typedef struct core_comm_UartInterface_callbacks_t {
	core_utils_Callback<void, void> rx;
	core_utils_Callback<void, core_comm_SerialMessage*> rx_msg;
} core_comm_UartInterface_callbacks_t;

/* ---------------------------------------------------------- */
typedef struct core_comm_UartInterface_config_t {
	core_hardware_UART_config uart;
	uint8_t use_protocol;
	uint8_t use_queue;
} core_comm_UartInterface_config_t;

/* ---------------------------------------------------------- */
extern core_hardware_UART_config std_hardware_uart_config;
extern core_comm_UartInterface_config_t std_uart_config;
/* ---------------------------------------------------------- */
class UartInterface {
public:
	UartInterface() {

	}
	virtual void rx_function() {
//		return 0;
	}
	virtual void setTaskID(TaskHandle_t task) {

	}
	virtual TaskHandle_t getTaskID() {
		return NULL;
	}
	uint8_t exit = 0;
};

/* ---------------------------------------------------------- */
void core_comm_SerialSocket_RTOS_Task(void *SerialSocket);

/* ---------------------------------------------------------- */
template<int uart_buffers, int uart_buffer_size>
class core_comm_UartInterface: public UartInterface {
public:

	core_comm_UartInterface_config_t config;
	core_comm_UartInterface_status_t status;
	core_comm_MessageQueue<uart_buffers, uart_buffer_size> rx_queue;

	/* ------------------------------------------------------------- */
	core_comm_UartInterface() {
		this->status = CORE_COMM_SERIAL_SOCKET_STATE_NONE;
		this->exit = 0;
	}
	/* ------------------------------------------------------------- */
	void init(UART_HandleTypeDef *huart) {
		this->init(huart, std_uart_config);
	}
	/* ------------------------------------------------------------- */
	void init(UART_HandleTypeDef *huart,
			core_comm_UartInterface_config_t config) {

		this->config = config;
		this->_uart.init(huart, this->config.uart);

		// Add the rx callback to the UARTs
		this->_uart.registerCallback(CORE_HARDWARE_UART_CB_RX,
				core_utils_Callback<void, void>(this,
						&core_comm_UartInterface<uart_buffers, uart_buffer_size>::rx_function));

		this->status = CORE_COMM_SERIAL_SOCKET_STATE_INIT;
	}
	/* ------------------------------------------------------------- */
	void start() {
		this->_uart.start();
		this->status = CORE_COMM_SERIAL_SOCKET_STATE_RUN;
//		this->_startRTOS();
	}
	/* ------------------------------------------------------------- */
	void reset(){
		this->_uart.reset();
	}
	/* ------------------------------------------------------------- */
	void send(core_comm_SerialMessage *message) {
		uint8_t len = message->encode(this->_tx_buf);
		this->send(this->_tx_buf, len);
	}
	/* ------------------------------------------------------------- */
	void send(uint8_t *buffer, uint16_t len) {
		if (this->status != CORE_COMM_SERIAL_SOCKET_STATE_RUN) {
			core_ErrorHandler(1);
		}

		this->_uart.send(buffer, len);
	}
	/* ------------------------------------------------------------- */
	void sendRaw(uint8_t *buffer, uint16_t len) {
		if (this->status != CORE_COMM_SERIAL_SOCKET_STATE_RUN) {
			core_ErrorHandler(1);
		}

		this->_uart.sendRaw(buffer, len);
	}
	/* ------------------------------------------------------------- */
	core_comm_SerialMessage getMessage() {
		return this->rx_queue.read();
	}
	/* ------------------------------------------------------------- */
	core_comm_SerialMessage* getMessagePointer() {
		return this->rx_queue.readPointer();
	}
	/* ------------------------------------------------------------- */
	void registerCallback(core_comm_UartInterface_callback_id_t callback_id,
			core_utils_Callback<void, void> callback) {
		switch (callback_id) {
		case CORE_COMM_SERIAL_SOCKET_CB_RX: {
			this->_callbacks.rx = callback;
			break;
		}
		case CORE_COMM_SERIAL_SOCKET_CB_RX_MSG: {
			core_ErrorHandler(0x00);
			break;
		}
		case CORE_COMM_SERIAL_SOCKET_CB_ERROR: {
			break;
		}
		}
	}
	/* ------------------------------------------------------------- */
	void registerCallback(core_comm_UartInterface_callback_id_t callback_id,
			core_utils_Callback<void, core_comm_SerialMessage*> callback) {
		switch (callback_id) {
		case CORE_COMM_SERIAL_SOCKET_CB_RX: {
			core_ErrorHandler(0x00);
			break;
		}
		case CORE_COMM_SERIAL_SOCKET_CB_RX_MSG: {
			this->_callbacks.rx_msg = callback;
			break;
		}
		case CORE_COMM_SERIAL_SOCKET_CB_ERROR: {
			core_ErrorHandler(0x00);
			break;
		}
		}
	}
	/* ------------------------------------------------------------- */
	void setTaskID(TaskHandle_t task) {
		this->_task_id = task;
	}

	/* ------------------------------------------------------------- */
	TaskHandle_t getTaskID() {
		return this->_task_id;
	}

	/* ------------------------------------------------------------- */
	void rx_function() {
		uint8_t num_messages = 0;

		while (this->_uart.available() > 0) {
			Buffer *buffer = this->_uart.rx_queue.read();

			if (this->config.use_protocol) {
				// Decode the buffer into the rx message
				uint8_t correct_message = this->_rx_msg.decode(buffer);

				// If the buffer did not contain a correct message do not proceed with the message handling
				if (!correct_message) {
					continue;
				}

				if (this->config.use_queue) {
					this->rx_queue.write(&_rx_msg);
				}

				if (this->_callbacks.rx.registered) {
					this->_callbacks.rx.call();
				}
				if (this->_callbacks.rx_msg.registered) {
					this->_callbacks.rx_msg.call(&_rx_msg);
				}
			} else { // no protocol used
				while (1) {
					nop();
				}
			}

			num_messages++;

		}
//		return num_messages;
	}

private:
	core_comm_SerialMessage _rx_msg;
	core_hardware_UART<uart_buffers, uart_buffer_size> _uart;
	uint8_t _tx_buf[uart_buffer_size];
	core_comm_UartInterface_callbacks_t _callbacks;
	osThreadId_t _thread_id = NULL;
	TaskHandle_t _task_id = NULL;
	/* ------------------------------------------------------------- */
//	void _startRTOS() {
//		const osThreadAttr_t task_attributes =
//				{ .name = "socket_task", .stack_size =
//				CORE_COMM_SERIAL_SOCKET_RTOS_RX_STACKSIZE, .priority =
//						(osPriority_t) CORE_COMM_SERIAL_SOCKET_RTOS_RX_PRIORITY };
//
//		this->_thread_id = osThreadNew(core_comm_SerialSocket_RTOS_Task, this,
//				&task_attributes);
//	}
//	/* ------------------------------------------------------------- */
//	void _rxNotify_callback() {
//		if (this->_task_id != NULL) {
//			BaseType_t xHigherPriorityTaskWoken = pdFALSE;
//			vTaskNotifyGiveFromISR(this->_task_id, &xHigherPriorityTaskWoken);
//			portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
//		}
//	}

};

#endif
#endif /* CORE_COMMUNICATION_SERIAL_SOCKET_H_ */
