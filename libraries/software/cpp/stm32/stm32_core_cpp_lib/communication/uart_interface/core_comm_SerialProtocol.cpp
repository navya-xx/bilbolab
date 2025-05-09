/*
 * serial_protocol.cpp
 *
 *  Created on: 8 Jul 2022
 *      Author: Dustin Lehmann
 */

#include "core_comm_SerialProtocol.h"

void core_comm_SerialMessage::copyTo(core_comm_SerialMessage *msg) {
	msg->tick = this->tick;
	msg->address_1 = this->address_1;
	msg->address_2 = this->address_2;
	msg->address_3 = this->address_3;
	msg->cmd = this->cmd;
	msg->len = this->len;

	for (int i = 0; i < len; i++) {
		msg->data_ptr[i] = this->data_ptr[i];
	}
}

uint8_t core_comm_SerialMessage::encode(uint8_t *buffer) {
	buffer[0] = CORE_SERIAL_MESSAGE_HEADER;
	uint32_to_bytearray(this->tick, &buffer[1]);
	buffer[5] = this->cmd;
	buffer[6] = this->address_1;
	buffer[7] = this->address_2;
	buffer[8] = this->address_3;
	buffer[9] = this->flag;
	buffer[10] = this->len >> 8;
	buffer[11] = this->len & 0xFF;

	for (uint8_t i = 0; i < this->len; i++) {
		buffer[12 + i] = this->data_ptr[i];
	}
	buffer[12 + this->len] = 0; // CRC8
	return CORE_SERIAL_MESSAGE_PROTOCOL_OVERHEAD + this->len;
//	CORE_SERIAL_MESSAGE_PROTOCOL_OVERHEAD + this->len;
}

void core_comm_SerialMessage::encode(Buffer *buffer) {
	buffer->data_ptr[0] = CORE_SERIAL_MESSAGE_HEADER;
	uint32_to_bytearray(this->tick, &buffer->data_ptr[1]);
	buffer->data_ptr[5] = this->cmd;
	buffer->data_ptr[6] = this->address_1;
	buffer->data_ptr[7] = this->address_2;
	buffer->data_ptr[8] = this->address_3;
	buffer->data_ptr[9] = this->flag;

	buffer->data_ptr[10] = this->len >> 8;
	buffer->data_ptr[11] = this->len & 0xFF;

	for (uint8_t i = 0; i < this->len; i++) {
		buffer->data_ptr[12 + i] = this->data_ptr[i];
	}
	buffer->data_ptr[12 + this->len] = 0; // CRC8
	buffer->len = this->len;
}

uint8_t core_comm_SerialMessage::check(uint8_t *buffer, uint16_t len) {

	if (len < CORE_SERIAL_MESSAGE_PROTOCOL_OVERHEAD) {
		return CORE_ERROR;
	}

	/* Check for the header */
	if (!(buffer[0] == CORE_SERIAL_MESSAGE_HEADER)) {
		return CORE_ERROR;
	}

//	if (!(buffer[len - 1] == CORE_SERIAL_MESSAGE_FOOTER)) {
//		return CORE_ERROR;
//	}

	/* Extract the data length */
	// Check if the data length matches with the length of the message
	uint16_t data_len = uint8_to_uint16(buffer[10], buffer[11]);
	if ((len - data_len) == CORE_SERIAL_MESSAGE_PROTOCOL_OVERHEAD) {
	} else {
		return CORE_ERROR;
	}

	return CORE_OK;

}
uint8_t core_comm_SerialMessage::check(Buffer *buffer) {
	return this->check(buffer->data_ptr, buffer->len);
}

uint8_t core_comm_SerialMessage::decode(uint8_t *buffer, uint16_t len) {
	if (this->check(buffer, len) == CORE_ERROR) {
		return CORE_ERROR;
	}

	/* Extract the command */


	/* Extract the tick */
	this->tick = bytearray_to_uint32(&buffer[1]);

	this->cmd = buffer[5];

	/* Extract the address */
	this->address_1 = buffer[6];
	this->address_2 = buffer[7];
	this->address_3 = buffer[8];

	/* Flag */
	this->flag = buffer[9];

	/* Extract the data length */
	this->len = uint8_to_uint16(buffer[10], buffer[11]);

	/* Extract the data */
	for (uint8_t i = 0; i < this->len; i++) {
		this->data_ptr[i] = buffer[i + 12];
	}

	return CORE_OK;
}

uint8_t core_comm_SerialMessage::decode(Buffer *buffer) {
	return this->decode(buffer->data_ptr, buffer->len);
}

