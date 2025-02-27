/*
 * core_messages.c
 *
 *  Created on: 18 Apr 2022
 *      Author: Dustin Lehmann
 */

#include "core_messages.h"

/* Parses a given message buffer into a core_message_t struct. Assumes that the buffer contains a message from header 0 to footer */
uint8_t core_comm_Message_Decode(uint8_t *buffer, uint16_t len,
		core_comm_Message_t *msg) {

	/* Check the message */
	uint8_t ret = core_comm_Message_Check(buffer, len);

	if (ret == CORE_ERROR){
		return CORE_ERROR;
	}

	/* Extract the address */
	msg->address_1 = buffer[1];
	msg->address_2 = buffer[2];

	/* Extract the command */
	msg->cmd = buffer[3];

	/* Extract the message ID */
	msg->msg = buffer[4];

	/* Extract the data length */
	msg->data_len = buffer[5];

	/* Extract the data */
	uint8_t data_idx = 6;

	for (uint8_t i = 0; i < msg->data_len; i++) {
		msg->data[i] = buffer[i + data_idx];
	}

	return CORE_OK;
}

/* Checks if the buffer contains a message. If so, it returns the layer ID */
uint8_t core_comm_Message_Check(uint8_t *buffer, uint16_t len) {

	uint8_t retval = CORE_OK;

	if (len < CORE_CONFIG_MSG_MIN_LEN) {
		return CORE_ERROR;
	}

	/* Check for the header */
	if (!(buffer[0] == CORE_CONFIG_MSG_HEADER)) {
		return CORE_ERROR;
	}

	if (!(buffer[len - 1] == CORE_CONFIG_MSG_FOOTER)) {
		return CORE_ERROR;
	}

	/* Extract the data length */
	// Check if the data length matches with the length of the message
	uint8_t data_len = buffer[5];
	if ((len - data_len) == 8) {
	} else {
		return CORE_ERROR;
	}

	return retval;
}

uint8_t core_comm_Message_Encode(core_comm_Message_t *msg, uint8_t *buffer) {
	buffer[0] = CORE_CONFIG_MSG_HEADER;
	buffer[1] = msg->address_1;
	buffer[2] = msg->address_2;
	buffer[3] = msg->cmd;
	buffer[4] = msg->msg;
	buffer[5] = msg->data_len;

	for (uint8_t i = 0; i < msg->data_len; i++) {
		buffer[6 + i] = msg->data[i];
	}
	buffer[6 + msg->data_len] = 0;
	buffer[7 + msg->data_len] = CORE_CONFIG_MSG_FOOTER;
	return 8 + msg->data_len;
}

/* MESSAGE QUEUES */

uint8_t core_comm_MsgQueue_Init(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *messages, uint8_t len) {

	msg_queue->messages = messages;
	msg_queue->len = len;
	return CORE_OK;
}

int8_t core_comm_MsgQueue_Available(core_comm_MsgQueue_t *msg_queue) {
	if (msg_queue->overflow) {
		return CORE_ERROR_MSG_QUEUE_OVERFLOW;
	}
	int8_t available_msg = msg_queue->idx_write - msg_queue->idx_read;
	if (available_msg < 0) {
		available_msg += msg_queue->len;
	}
	return available_msg;
}

uint8_t core_comm_MsgQueue_Write(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *msg) {
	msg_queue->messages[msg_queue->idx_write] = *msg;

	return core_comm_MsgQueue_IncWrite(msg_queue);
}

uint8_t core_comm_MsgQueue_Read(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *msg) {
	if (core_comm_MsgQueue_Available(msg_queue)
			== 0|| core_comm_MsgQueue_Available(msg_queue) == CORE_ERROR_MSG_QUEUE_OVERFLOW) {
		return 0;
	}
	*msg = msg_queue->messages[msg_queue->idx_read];

	core_comm_MsgQueue_IncRead(msg_queue);

	return CORE_OK;
}

core_comm_Message_t* core_comm_MsgQueue_ReadPointer(core_comm_MsgQueue_t *msg_queue) {
	if (core_comm_MsgQueue_Available(msg_queue)
			== 0|| core_comm_MsgQueue_Available(msg_queue) == CORE_ERROR_MSG_QUEUE_OVERFLOW) {
		return 0;
	}

	core_comm_Message_t *ret = &msg_queue->messages[msg_queue->idx_read];
	core_comm_MsgQueue_IncRead(msg_queue);

	return ret;
}

uint8_t core_comm_MsgQueue_ReadNoInc(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *msg) {
	if (core_comm_MsgQueue_Available(msg_queue)
			== 0|| core_comm_MsgQueue_Available(msg_queue) == CORE_ERROR_MSG_QUEUE_OVERFLOW) {
		return 0;
	}
	*msg = msg_queue->messages[msg_queue->idx_read];

	return CORE_OK;
}
uint8_t core_comm_MsgQueue_ReadPointerNoInc(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *msg) {
	if (core_comm_MsgQueue_Available(msg_queue)
			== 0|| core_comm_MsgQueue_Available(msg_queue) == CORE_ERROR_MSG_QUEUE_OVERFLOW) {
		return 0;
	}
	msg = &msg_queue->messages[msg_queue->idx_read];

	return CORE_OK;
}

core_comm_Message_t* core_comm_MsgQueue_GetPointerForWriting(
		core_comm_MsgQueue_t *msg_queue) {
	uint8_t idx_out = msg_queue->idx_write;
	if (idx_out == msg_queue->len) {
		idx_out = 0;
	}
	return &msg_queue->messages[idx_out];
}

uint8_t core_comm_MsgQueue_IncWrite(core_comm_MsgQueue_t *msg_queue) {
	msg_queue->idx_write++;

	if (msg_queue->idx_write == msg_queue->len) {
		msg_queue->idx_write = 0;
	}

	if (msg_queue->idx_write == msg_queue->idx_read) {
		msg_queue->overflow = 1;
		return 0;
	}
	return CORE_OK;
}

uint8_t core_comm_MsgQueue_IncRead(core_comm_MsgQueue_t *msg_queue) {
	msg_queue->idx_read++;
	if (msg_queue->idx_read == msg_queue->len) {
		msg_queue->idx_read = 0;
	}

	return CORE_OK;
}

uint8_t core_comm_MsgQueue_Clear(core_comm_MsgQueue_t *msg_queue) {
	msg_queue->idx_read = 0;
	msg_queue->idx_write = 0;
	msg_queue->overflow = 0;

	return CORE_OK;
}

///* MESSAGE HANDLERS */
//
//uint8_t core_comm_msg_MessageHandler(core_comm_Message_t *msg) {
//
//	uint8_t ret = CORE_ERROR_MSG_ID_NOT_FOUND;
//
//	switch (msg->cmd) {
//
//	case CORE_MSG_TYPE_WRITE:
//		ret = core_comm_msg_MessageHandlerWrite(msg);
//		break;
//	}
//
//	return ret;
//}
//
//uint8_t core_comm_msg_MessageHandlerWrite(core_comm_Message_t *msg) {
//	uint8_t ret = CORE_ERROR_MSG_ID_NOT_FOUND;
//
//	switch (msg->msg) {
//	case MSG_STM32_CORE_WRITE_Register: {
//		ret = CORE_ERROR_MSG_ID_NOT_IMPLEMENTED;
//		break;
//	}
//	case CORE_MSG_WRITE_ID_Led: {
//		ret = core_comm_msg_handler_write_Led(msg);
//		break;
//	}
//	}
//
//	return ret;
//}
//
///* This message writes one of the discrete LEDs connected to the STM32
// *
// * Length: 2
// *
// * |Byte	|Name		|Data type		|Description								|
// * |0		|led_num	|uint8			|ID of the LED supposed to be written 		|
// * |1		|state		|int8 			|State of the LED. 0: off, 1: on, -1: toggle |
// *
// */
//uint8_t core_comm_msg_handler_write_Led(core_comm_Message_t *msg) {
//
//	if (!(msg->data_len == CORE_MSG_WRITE_LEN_Led)) {
//		return CORE_ERROR_MSG_WRONG_LENGTH;
//	}
//
//	core_Board_SetLed(msg->data[0], msg->data[1]);
//
//	return CORE_OK;
//}
