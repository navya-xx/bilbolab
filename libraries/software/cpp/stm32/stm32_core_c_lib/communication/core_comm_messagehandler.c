/*
 * core_message_handler.c
 *
 *  Created on: 19 Apr 2022
 *      Author: Dustin Lehmann
 */

#include "core_comm_messagehandler.h"

void test_fun(core_comm_Message_t *msg, void *params) {

}

void test_fun2(core_comm_Message_t *msg, void *params) {

}

void test_fun3(core_comm_Message_t *msg, void *params) {

}

uint8_t core_comm_MsgHandler_Init(core_comm_MsgHandler_t *msg_handler) {
	if (msg_handler->Init.socket != NULL) {
		msg_handler->socket = msg_handler->Init.socket;
	} else {
		core_ErrorHandler(0);
	}

	if (msg_handler->Init.rx_msg_queue != NULL) {
		msg_handler->rx_msg_queue = msg_handler->Init.rx_msg_queue;
	}

	if (msg_handler->Init.layer != 0) {
		msg_handler->layer = msg_handler->Init.layer;
	}

	for (int i = 0; i < msg_handler->Init.num_WriteMessages; i++) {
		uint8_t id = msg_handler->Init.WriteMessages[i].id;
		if (id < CORE_COMM_MSGHANDLER_MAX_ID_WRITE
				&& !msg_handler->write[id].set) {
			msg_handler->write[id] = msg_handler->Init.WriteMessages[i];
		} else {
			core_ErrorHandler(0);
		}
	}
	for (int i = 0; i < msg_handler->Init.num_RequestMessages; i++) {
		uint8_t id = msg_handler->Init.RequestMessages[i].id;
		if (id < CORE_COMM_MSGHANDLER_MAX_ID_READ
				&& !msg_handler->request[id].set) {
			msg_handler->request[id] = msg_handler->Init.RequestMessages[i];
		} else {
			core_ErrorHandler(0);
		}
	}

//	// Set the Socket correctly
//	switch (msg_handler->layer) {
//	case (CORE_MSG_LAYER_CORE): {
//		msg_handler->socket->msg_queues.rx_queue_core =
//				msg_handler->rx_msg_queue;
//		core_comm_Socket_RegisterCallback(msg_handler->socket,
//				CORE_COMM_SOCKET_CB_RX_MSG_CORE,
//				_core_comm_MsgHandler_RTOS_RxNotify_CB, msg_handler);
//		break;
//	}
//	case (CORE_MSG_LAYER_ROBOT): {
//		msg_handler->socket->msg_queues.rx_queue_robot =
//				msg_handler->rx_msg_queue;
//		core_comm_Socket_RegisterCallback(msg_handler->socket,
//				CORE_COMM_SOCKET_CB_RX_MSG_ROBOT,
//				_core_comm_MsgHandler_RTOS_RxNotify_CB, msg_handler);
//		break;
//	}
//	}

	return CORE_OK;
}

void core_comm_MsgHandler_RTOS_Start(core_comm_MsgHandler_t *msg_handler) {
//	const osThreadAttr_t task_attributes = { .name = "",
//			.stack_size = CORE_COMM_SOCKET_RTOS_RX_STACKSIZE, .priority =
//					(osPriority_t) CORE_COMM_SOCKET_RTOS_RX_PRIORITY };
//
//	socket->RTOS.rx_task_handle = osThreadNew(core_comm_Socket_RTOS_RxTask,
//			socket, &rx_task_attributes);
}

uint8_t core_comm_MsgHandler_HandleMsg(core_comm_MsgHandler_t *msg_handler,
		core_comm_Message_t *msg) {
	if (msg->cmd == CORE_MSG_TYPE_WRITE) {
		if (msg_handler->write[msg->msg].set) {
			msg_handler->write[msg->msg].function(msg,
					msg_handler->write[msg->msg].params);
			return CORE_OK;
		}
	} else if (msg->cmd == CORE_MSG_TYPE_REQUEST) {
		if (msg_handler->request[msg->msg].set) {
			msg_handler->request[msg->msg].function(msg,
					msg_handler->request[msg->msg].params);
			return CORE_OK;
		}
	}
	return CORE_ERROR;
}

void core_comm_MsgHandler_RTOS_Task(void *argument) {
	while (1) {
		// Wait until the task is notified
		uint32_t ulNotificationValue = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
		if (ulNotificationValue) {

		}
	}
}

void _core_comm_MsgHandler_RTOS_RxNotify_CB(void *argument, void *_msg_handler) {
	core_comm_MsgHandler_t *msg_handler = (core_comm_MsgHandler_t*) _msg_handler;
	if (msg_handler->RTOS.rx_task_handle) {
		BaseType_t xHigherPriorityTaskWoken = pdFALSE;
		vTaskNotifyGiveFromISR(msg_handler->RTOS.rx_task_handle,
				&xHigherPriorityTaskWoken);
		portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
	}

}
