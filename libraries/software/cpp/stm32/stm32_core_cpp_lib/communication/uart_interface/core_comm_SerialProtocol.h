/*
 * serial_protocol.h
 *
 *  Created on: 8 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_COMMUNICATION_SERIAL_SOCKET_CORE_COMM_SERIALPROTOCOL_H_
#define CORE_COMMUNICATION_SERIAL_SOCKET_CORE_COMM_SERIALPROTOCOL_H_

#include "stdint.h"
#include "../../core_includes.h"
#include "../../utils/core_utils.h"

#define CORE_SERIAL_MESSAGE_HEADER 0x55
#define CORE_SERIAL_MESSAGE_PROTOCOL_OVERHEAD 9

class core_comm_SerialMessage {
public:
	uint8_t cmd;
	uint8_t address_1;
	uint8_t address_2;
	uint8_t address_3;
	uint8_t flag;
	uint8_t *data_ptr;
	uint16_t len;

	void copyTo(core_comm_SerialMessage *msg);
	uint8_t check(uint8_t *buffer, uint16_t len);
	uint8_t check(Buffer *buffer);
	uint8_t encode(uint8_t *buffer);
	void encode(Buffer *buffer);
	uint8_t decode(uint8_t *buffer, uint16_t len);
	uint8_t decode(Buffer *buffer);

private:
};

template <int size>
class core_comm_SerialMessage_memory: public core_comm_SerialMessage {
public:
	core_comm_SerialMessage_memory(){
		this->data_ptr = data;
	}
	uint8_t data[size];
};

#endif /* CORE_COMMUNICATION_SERIAL_SOCKET_CORE_COMM_SERIALPROTOCOL_H_ */
