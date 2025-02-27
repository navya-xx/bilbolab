/*
 * twipr_communication.h
 *
 *  Created on: Feb 22, 2023
 *      Author: lehmann_workstation
 */

#ifndef COMMUNICATION_TWIPR_UART_COMMUNICATION_H_
#define COMMUNICATION_TWIPR_UART_COMMUNICATION_H_

#include "core.h"
#include "twipr_messages.h"

#define TWIPR_UART_COMM_QUEUE_SIZE 10
#define TWIPR_UART_COMM_BUF_SIZE 128

#define MSG_COMMAND_WRITE 0x01
#define MSG_COMMAND_READ 0x02
#define MSG_COMMAND_ANSWER 0x03
#define MSG_COMMAND_STREAM 0x04
#define MSG_COMMAND_EVENT 0x05
#define MSG_COMMAND_MSG 0x06
#define MSG_COMMAND_FCT 0x07
#define MSG_COMMAND_ECHO 0x08


typedef struct twipr_uart_comm_config_t {
	UART_HandleTypeDef *huart;
} twipr_uart_comm_config_t;

typedef enum twipr_uart_comm_callback_id_t {
	TWIPR_UART_COMM_CALLBACK_RX_MSG,
	TWIPR_UART_COMM_CALLBACK_MSG_WRITE,
	TWIPR_UART_COMM_CALLBACK_MSG_READ,
	TWIPR_UART_COMM_CALLBACK_MSG_FUNC,
} twipr_uart_comm_callback_id_t;

typedef struct twipr_uart_comm_callbacks_t {
	core_utils_Callback<void, core_comm_SerialMessage*> rx_msg;
	core_utils_Callback<void, core_comm_SerialMessage*> write_msg;
	core_utils_Callback<void, core_comm_SerialMessage*> read_msg;
	core_utils_Callback<void, core_comm_SerialMessage*> func_msg;
} twipr_uart_comm_callbacks_t;


class TWIPR_UART_Communication {
public:

	xTaskHandle task;
	uint32_t last_received_message_tick = 0;

	TWIPR_UART_Communication();

	void init(twipr_uart_comm_config_t config);
	void start();
	void reset();
	void send(core_comm_SerialMessage msg);
	void send(core_comm_SerialMessage *msg);
	void send(uint8_t cmd, uint8_t module, uint16_t address, uint8_t flag,
			uint8_t *data, uint8_t len);

	void sendRaw(uint8_t *buffer, uint16_t len);

	void registerCallback(twipr_uart_comm_callback_id_t callback_id,
			core_utils_Callback<void, core_comm_SerialMessage*> callback);

	void taskFunction();

private:
	osThreadId_t _thread;
	void _rx_callback();
	void _handleIncomingMessages();
	void _handleMessage_read(core_comm_SerialMessage *msg);
	void _handleMessage_write(core_comm_SerialMessage *msg);
	void _handleMessage_function(core_comm_SerialMessage *msg);
	core_comm_UartInterface<TWIPR_UART_COMM_QUEUE_SIZE, TWIPR_UART_COMM_BUF_SIZE> _uart_cm4;

	RegisterMap *register_map;
	twipr_uart_comm_callbacks_t _callbacks;
};

#endif /* COMMUNICATION_TWIPR_UART_COMMUNICATION_H_ */
