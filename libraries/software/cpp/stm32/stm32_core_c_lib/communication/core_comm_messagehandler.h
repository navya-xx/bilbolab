/*
 * core_message_handler.h
 *
 *  Created on: 19 Apr 2022
 *      Author: Dustin Lehmann
 */

#ifndef COMMUNICATION_CORE_COMM_MESSAGEHANDLER_H_
#define COMMUNICATION_CORE_COMM_MESSAGEHANDLER_H_

#include "core_messages.h"
#include "core_comm_socket.h"

#include <cmsis_os.h>


#define CORE_COMM_MSGHANDLER_MAX_ID_WRITE 128
#define CORE_COMM_MSGHANDLER_MAX_ID_READ 128

typedef enum core_comm_MsgHandler_Entry_Prio_t {
	CORE_COMM_MSGHANDLER_ENTRY_PRIO_HIGH = 1,
	CORE_COMM_MSGHANDLER_ENTRY_PRIO_LOW = 2,
	CORE_COMM_MSGHANDLER_ENTRY_PRIO_BLOCKING = 3
} core_comm_MsgHandler_Entry_Prio_t;

typedef struct core_comm_MsgHandler_Entry_t {
	uint8_t id;
	void (*function)(core_comm_Message_t *msg, void *params);
	void *params;
	core_comm_MsgHandler_Entry_Prio_t priority;
	uint8_t set;
} core_comm_MsgHandler_Entry_t;

typedef struct core_comm_MsgHandler_Init_t {
	core_comm_Socket_t *socket;
	core_comm_MsgHandler_Entry_t *WriteMessages;
	uint8_t num_WriteMessages;
	core_comm_MsgHandler_Entry_t *RequestMessages;
	uint8_t num_RequestMessages;
	core_comm_MsgQueue_t *rx_msg_queue;
	uint8_t layer;
} core_comm_MsgHandler_Init_t;

typedef struct core_comm_MsgHandlerCore_RTOS_t {
	osThreadId_t rx_task_handle;
} core_comm_MsgHandlerCore_RTOS_t;

typedef struct core_comm_MsgHandler_t {
	core_comm_Socket_t *socket;
	core_comm_MsgQueue_t *rx_msg_queue;
	uint8_t layer;

	core_comm_MsgHandler_Entry_t write[CORE_COMM_MSGHANDLER_MAX_ID_WRITE];
	core_comm_MsgHandler_Entry_t request[CORE_COMM_MSGHANDLER_MAX_ID_READ];

	core_comm_MsgHandlerCore_RTOS_t RTOS;
	core_comm_MsgHandler_Init_t Init;
} core_comm_MsgHandler_t;

uint8_t core_comm_MsgHandler_Init(core_comm_MsgHandler_t *msg_handler);
uint8_t core_comm_MsgHandler_Start(core_comm_MsgHandler_t *msg_handler);

uint8_t core_comm_MsgHandler_HandleMsg(
		core_comm_MsgHandler_t *msg_handler, core_comm_Message_t *msg);

uint8_t core_comm_MsgHandler_RegisterCallback(
		core_comm_MsgHandler_t *msg_handler,
		core_comm_socket_CallbackID_t callback_id,
		void (*callback)(void *argument, void *params), void *params);

uint8_t core_comm_MsgHandler_SetFilter();

uint8_t core_comm_MsgHandler_SetHandler(
		core_comm_MsgHandler_t *msg_handler, uint8_t id,
		void (*handler)(core_comm_Message_t *msg, void *params));


void core_comm_MsgHandler_RTOS_Start(
		core_comm_MsgHandler_t *msg_handler);
void core_comm_MsgHandler_RTOS_Task(void *msg_handler);
void _core_comm_MsgHandler_RTOS_RxNotify_CB(void *argument,
		void *_msg_handler);

void test_fun(core_comm_Message_t *msg, void *params);
void test_fun2(core_comm_Message_t *msg, void *params);
void test_fun3(core_comm_Message_t *msg, void *params);

#endif /* COMMUNICATION_CORE_COMM_MESSAGEHANDLER_H_ */
