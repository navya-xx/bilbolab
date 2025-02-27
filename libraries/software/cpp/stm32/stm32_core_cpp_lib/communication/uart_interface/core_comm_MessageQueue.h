/*
 * core_comm_MessageQueue.h
 *
 *  Created on: 8 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_COMMUNICATION_SERIAL_SOCKET_CORE_COMM_MESSAGEQUEUE_H_
#define CORE_COMMUNICATION_SERIAL_SOCKET_CORE_COMM_MESSAGEQUEUE_H_

#include <communication/uart_interface/core_comm_SerialProtocol.h>

template<int num_messages, int buf_size>
class core_comm_MessageQueue {
public:

	void init() {
		this->idx_read = 0;
		this->idx_write = 0;
		this->overflow = 0;
	}

	uint8_t inc_write() {
		this->idx_write++;
		if (this->idx_write == this->len) {
			this->idx_write = 0;
		}
		// TODO: overflow
		return this->idx_write;
	}
	uint8_t inc_read() {
		this->idx_read++;
		if (this->idx_read == this->len) {
			this->idx_read = 0;
		}
		return this->idx_read;
	}

	uint8_t write(core_comm_SerialMessage *message) {
		message->copyTo(&this->messages[this->idx_write]);
		return this->inc_write();
	}

	uint8_t read(core_comm_SerialMessage *message) {
		if (this->available() < 1) {
			return 0;
		}

//		*message = this->messages[this->idx_read];
		message->address_1 = this->messages[this->idx_read].address_1;
		message->address_2 = this->messages[this->idx_read].address_2;
		message->address_3 = this->messages[this->idx_read].address_3;
		message->flag = this->messages[this->idx_read].flag;
		message->cmd = this->messages[this->idx_read].cmd;
		message->len = this->messages[this->idx_read].len;

		for (int i = 0; i<message->len; i++){
			message->data_ptr[i] = this->messages[this->idx_read].data_ptr[i];
		}

		this->inc_read();
		return 1;
	}

	core_comm_SerialMessage read() {
		core_comm_SerialMessage msg;
		this->read(&msg);
		return msg;
	}

	core_comm_SerialMessage* readPointer() {
		core_comm_SerialMessage *msg = &this->messages[this->idx_read];
		this->inc_read();
		return msg;
	}

	uint8_t available() {
		int8_t available_msg = this->idx_write - this->idx_read;
		if (available_msg < 0) {
			available_msg += this->len;
		}
		return available_msg;
	}
	core_comm_SerialMessage_memory<buf_size> messages[num_messages];
private:
	uint8_t idx_read;
	uint8_t idx_write;
	uint8_t overflow;
	uint8_t len = num_messages;
};

#endif /* CORE_COMMUNICATION_SERIAL_SOCKET_CORE_COMM_MESSAGEQUEUE_H_ */
