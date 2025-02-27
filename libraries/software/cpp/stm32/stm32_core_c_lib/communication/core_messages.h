/*
 * core_messages.h
 *
 *  Created on: 18 Apr 2022
 *      Author: Dustin Lehmann
 */

#ifndef COMMUNICATION_CORE_MESSAGES_H_
#define COMMUNICATION_CORE_MESSAGES_H_

#include "stdint.h"

#include "messages_def.h"
#include "config_core.h"
#include "core_board.h"

// I need a struct that hold the pointers to the message callback functions

#define CORE_ERROR_MSG_ID_NOT_FOUND 0x05
#define CORE_ERROR_MSG_ID_NOT_IMPLEMENTED 0x06
#define CORE_ERROR_MSG_WRONG_LENGTH 0x07

#define CORE_MSG_QUEUE_LENGTH 10
#define CORE_ERROR_MSG_QUEUE_OVERFLOW -1

typedef struct core_comm_Message_t {
	uint8_t cmd;
	uint8_t address_1;
	uint8_t address_2;
	uint8_t msg;
	uint8_t data[CORE_CONFIG_MSG_DATA_LENGTH_MAX];
	uint8_t data_len;
} core_comm_Message_t;

/* Message Queues */
typedef struct {
	uint8_t idx_read;
	uint8_t idx_write;
	core_comm_Message_t *messages;
	uint8_t overflow;
	uint8_t len;
} core_comm_MsgQueue_t;

uint8_t core_comm_MsgQueue_Init(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *messages, uint8_t len);
uint8_t core_comm_MsgQueue_Write(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *msg);
uint8_t core_comm_MsgQueue_Read(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *msg);

core_comm_Message_t* core_comm_MsgQueue_ReadPointer(
		core_comm_MsgQueue_t *msg_queue);

core_comm_Message_t* core_comm_MsgQueue_GetPointerForWriting(
		core_comm_MsgQueue_t *msg_queue);

uint8_t core_comm_MsgQueue_IncWrite(core_comm_MsgQueue_t *msg_queue);
uint8_t core_comm_MsgQueue_IncRead(core_comm_MsgQueue_t *msg_queue);

uint8_t core_comm_MsgQueue_ReadNoInc(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *msg);
uint8_t core_comm_MsgQueue_ReadPointerNoInc(core_comm_MsgQueue_t *msg_queue,
		core_comm_Message_t *msg);
uint8_t core_comm_MsgQueue_Clear(core_comm_MsgQueue_t *msg_queue);
int8_t core_comm_MsgQueue_Available(core_comm_MsgQueue_t *msg_queue);

/* Message parsing */

uint8_t core_comm_Message_Check(uint8_t *buffer, uint16_t len);

uint8_t core_comm_Message_Decode(uint8_t *buffer, uint16_t len,
		core_comm_Message_t *msg);
uint8_t core_comm_Message_Encode(core_comm_Message_t *msg, uint8_t *buffer);

#endif /* COMMUNICATION_CORE_MESSAGES_H_ */
