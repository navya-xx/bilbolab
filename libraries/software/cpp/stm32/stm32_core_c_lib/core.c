/*
 * core.c
 *
 *  Created on: 15 Apr 2022
 *      Author: Dustin Lehmann
 */

#include "core.h"

#include "config_messages.h"

/* === Communication === */

/* == UART == */

/* CM4 UART */
core_utils_Buffer_t core_CM4Uart_RxBuffer[20] _RAM_D2;
core_utils_Buffer_t core_CM4Uart_TxBuffer[20] _RAM_D2;
core_utils_BufferQueue_t core_CM4Uart_RxBufferQueue;
core_utils_BufferQueue_t core_CM4Uart_TxBufferQueue;

core_hardware_Uart_t core_CM4Uart;

/* CM4 Socket */
core_comm_Socket_t core_CM4Socket;

core_comm_Message_t core_CM4Socket_TxMsgBuffer[20] _RAM_D2 = { 0 };
core_comm_Message_t core_CM4Socket_RxMsgBuffer[20] _RAM_D2 = { 0 };
core_comm_MsgQueue_t core_CM4Socket_RxMsgQueue;
core_comm_MsgQueue_t core_CM4Socket_TxMsgQueue;

/* Core Message Handler */
core_comm_Message_t core_CoreMsgHandler_RxMsgBuffer[20] _RAM_D2 = { 0 };

core_comm_MsgQueue_t core_CoreMsgHandler_RxMsgQueue;
core_comm_MsgHandler_t core_CoreMsgHandler;



/* */
uint8_t core_Init(core_t *core) {
	/* UART */
	core_utils_BufferQueue_Init(&core_CM4Uart_RxBufferQueue,
								core_CM4Uart_RxBuffer,
								sizeof(core_CM4Uart_RxBuffer) / sizeof(core_CM4Uart_RxBuffer[0]));

	core_utils_BufferQueue_Init(&core_CM4Uart_TxBufferQueue,
								core_CM4Uart_TxBuffer,
								sizeof(core_CM4Uart_TxBuffer) / sizeof(core_CM4Uart_TxBuffer[0]));

	core_CM4Uart.Init.hdma_rx = core->HardwareInit.cm4_uart.hdma_rx;
	core_CM4Uart.Init.hdma_tx = core->HardwareInit.cm4_uart.hdma_tx;
	core_CM4Uart.Init.huart = core->HardwareInit.cm4_uart.huart;
	core_CM4Uart.Init.rx_queue = &core_CM4Uart_RxBufferQueue;
	core_CM4Uart.Init.tx_queue = &core_CM4Uart_TxBufferQueue;
	core_CM4Uart.Init.tx_cobs_encode = 1;
	core_CM4Uart.Init.rx_cobs_encode = 1;
	core_hardware_Uart_Init(&core_CM4Uart);

	/* CM4 Socket */
	core_comm_MsgQueue_Init(&core_CM4Socket_TxMsgQueue,
							core_CM4Socket_TxMsgBuffer,
							sizeof(core_CM4Socket_TxMsgBuffer)/(sizeof(core_CM4Socket_TxMsgBuffer[0])));

	core_comm_MsgQueue_Init(&core_CM4Socket_RxMsgQueue,
							core_CM4Socket_RxMsgBuffer,
							sizeof(core_CM4Socket_RxMsgBuffer)/(sizeof(core_CM4Socket_RxMsgBuffer[0])));

	core_CM4Socket.Init.uart = &core_CM4Uart;
	core_CM4Socket.Init.rx_msg_queue = &core_CM4Socket_RxMsgQueue;
	core_CM4Socket.Init.tx_msg_queue = &core_CM4Socket_TxMsgQueue;
	core_comm_Socket_Init(&core_CM4Socket);

	core->cm4_socket = &core_CM4Socket;

	/* Core Message Handler */
//	core_comm_MsgQueue_Init(&core_CoreMsgHandler_RxMsgQueue,
//							core_CoreMsgHandler_RxMsgBuffer,
//							sizeof(core_CoreMsgHandler_RxMsgBuffer)/(sizeof(core_CoreMsgHandler_RxMsgBuffer[0])));
//
//	core_CoreMsgHandler.Init.layer = CORE_MSG_LAYER_CORE;
//	core_CoreMsgHandler.Init.socket = &core_CM4Socket;
//	core_CoreMsgHandler.Init.rx_msg_queue = &core_CoreMsgHandler_RxMsgQueue;
//	core_CoreMsgHandler.Init.RequestMessages = core_CoreMsgHandler_RequestMessages;
//	core_CoreMsgHandler.Init.num_RequestMessages = sizeof(core_CoreMsgHandler_RequestMessages) / sizeof(core_CoreMsgHandler_RequestMessages[0]);
//	core_CoreMsgHandler.Init.WriteMessages = core_CoreMsgHandler_WriteMessages;
//	core_CoreMsgHandler.Init.num_WriteMessages = sizeof(core_CoreMsgHandler_WriteMessages) / sizeof(core_CoreMsgHandler_WriteMessages[0]);
//
//	core_comm_MsgHandler_Init(&core_CoreMsgHandler);

	core_comm_Socket_RTOS_Start(&core_CM4Socket);

	return CORE_OK;
}

