/*
 * communication.h
 *
 *  Created on: Apr 5, 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_INC_CORE_COMM_SOCKET_H_
#define CORE_INC_CORE_COMM_SOCKET_H_

#include <core_uart.h>
#include <core_usb.h>
#include <core_messages.h>
#include <core_utils.h>
#include <cmsis_os.h>

/* ======================================================================================= */
#define CORE_COMM_SOCKET_RX_INTERRUPT

#define CORE_COMM_SOCKET_RTOS
#define CORE_COMM_SOCKET_RTOS_RX_STACKSIZE 4000
#define CORE_COMM_SOCKET_RTOS_RX_PRIORITY osPriorityHigh

/* ======================================================================================= */
typedef enum {
	CORE_COMM_SOCKET_STATE_NONE = 0,
	CORE_COMM_SOCKET_STATE_INIT = 1,
	CORE_COMM_SOCKET_STATE_ACTIVE = 2,
	CORE_COMM_SOCKET_STATE_ERROR = 3
} core_comm_socket_state_t;

typedef enum {
	CORE_COMM_SOCKET_INTERFACE_UART = 1, CORE_COMM_SOCKET_INTERFACE_USB = 2
} core_comm_socket_Interface_t;

typedef struct core_comm_socket_Init_t {
	core_hardware_Uart_t *uart;
	core_comm_socket_Interface_t interface;
	core_comm_MsgQueue_t *tx_msg_queue;
	core_comm_MsgQueue_t *rx_msg_queue;
} core_comm_socket_Init_t;

typedef struct core_comm_socket_rtos_t {
	osThreadId_t rx_task_handle;
} core_comm_Socket_RTOS_t;

typedef enum core_comm_socket_CallbackID_t {
	CORE_COMM_SOCKET_CB_RX_MSG = 0,
	CORE_COMM_SOCKET_CB_RX_MSG_ROBOT = 2,
} core_comm_socket_CallbackID_t;

typedef struct core_comm_socket_Callbacks_t {
	core_utils_Callback_t rx_msg_robot;
	core_utils_Callback_t rx_msg;
} core_comm_socket_Callbacks_t;

typedef struct core_comm_socket_t {
	core_hardware_Uart_t *uart;
	core_comm_socket_Interface_t interface;
	core_comm_socket_state_t state;

	uint8_t tx_buf[255];

	core_comm_Message_t _rxMsg;  // temporary message parsed from the RX buffer of the UART

	core_comm_MsgQueue_t *tx_msg_queue;
	core_comm_MsgQueue_t *rx_msg_queue;  // Internal RX message queue

	core_comm_MsgQueue_t *rx_msg_queue_robot;  // TODO: Robot message queue

	core_comm_socket_Callbacks_t callbacks;

	core_comm_Socket_RTOS_t RTOS;
	core_comm_socket_Init_t Init;
} core_comm_Socket_t;

uint8_t core_comm_Socket_Init(core_comm_Socket_t *socket);
uint8_t core_comm_Socket_Start(core_comm_Socket_t *socket);

uint8_t core_comm_Socket_RxFunction(core_comm_Socket_t *socket);

uint8_t core_comm_Socket_RegisterCallback(core_comm_Socket_t *socket,
		core_comm_socket_CallbackID_t callback_id,
		void (*callback)(void *argument, void *params), void *params);

uint8_t core_comm_Socket_Send(core_comm_Socket_t *socket, uint8_t *data,
		uint8_t len);

uint8_t core_comm_Socket_SendMessage(core_comm_Socket_t *socket,
		core_comm_Message_t *msg);

uint8_t core_comm_Socket_SendMessageBlocking(core_comm_Socket_t *socket,
		core_comm_Message_t *msg, uint16_t timeout);

void _core_comm_Socket_TxCpltCallback(void *argument, void *params);
void _core_comm_Socket_SendNextMessage(core_comm_Socket_t *socket);
void _core_comm_Socket_RxCpltCallback(void *argument, void *uart);

void core_comm_Socket_RTOS_Start(core_comm_Socket_t *socket);
void core_comm_Socket_RTOS_RxTask(void *socket);

void _core_comm_Socket_RTOS_RxNotify_CB(void *argument, void *_socket);

#endif /* CORE_INC_CORE_COMM_SOCKET_H_ */

