/*
 * core_utils_BufferQueue.h
 *
 *  Created on: Jul 7, 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_UTILS_CORE_UTILS_BUFFERQUEUE_H_
#define CORE_UTILS_CORE_UTILS_BUFFERQUEUE_H_

#include "stdint.h"
#include "../core_default_config.h"

class Buffer {
public:
	Buffer() {

	}
	uint8_t* data_ptr;
	uint16_t len = 0;
};

template <int size>
class core_utils_Buffer: public Buffer {
public:
	core_utils_Buffer<size>(){
		this->data_ptr = this->buffer;
	}
	uint8_t buffer[size] = { 0 };
};

template<int num, int size>
class core_utils_BufferQueue {
public:
	core_utils_BufferQueue() {
		this->idx_read = 0;
		this->idx_write = 0;
		this->overflow = 0;
	}

	uint8_t overflow;

	uint8_t write(Buffer *buffer) {
		for (int i = 0; i < buffer->len; i++) {
			this->buffers[this->idx_write].data_ptr[i] = buffer->data_ptr[i];
		}

		this->buffers[this->idx_write].len = buffer->len;
		return this->inc_write();
	}

	uint8_t write(uint8_t *buffer, uint16_t len) {
		for (int i = 0; i < len; i++) {
			this->buffers[this->idx_write].data_ptr[i] = buffer[i];
		}
		this->buffers[this->idx_write].len = len;
		return this->inc_write();
	}

	Buffer* getWritePointer() {
		return &this->buffers[this->idx_write];
	}

	void finishWriting(uint8_t len) {
		this->buffers[this->idx_write].len = len;
		this->inc_write();
	}

	uint8_t read(Buffer *buffer) {
		if (this->available() < 1) {
			return 0;
		}
		*buffer = this->buffers[this->idx_read];
		this->inc_read();
		return 1;
	}
	uint8_t read(uint8_t *buffer) {
		if (this->available() < 1) {
			return 0;
		}
		for (int i = 0; i < this->buffers[this->idx_read].len; i++) {
			buffer[i] = this->buffers[this->idx_read].data_ptr[i];
		}

		uint8_t len = this->buffers[this->idx_read].len;
		this->inc_read();

		return len;
	}
	uint8_t read(uint8_t **buffer) {
		if (this->available() < 1) {
			return 0;
		}
		*buffer = &this->buffers[this->idx_read].data_ptr[0];

		uint8_t len = this->buffers[this->idx_read].len;
		this->inc_read();
		return len;
	}
	Buffer* read() {
		if (this->available() < 1) {
			return 0;
		}

		Buffer *buffer = &this->buffers[this->idx_read];
		this->inc_read();
		return buffer;
	}

	int8_t available() {
		if (this->overflow) {
			return -1;
		}
		int8_t available = this->idx_write - this->idx_read;
		if (available < 0) {
			available += this->num_buffers;
		}
		return available;

	}
	void clear() {
		this->idx_read = 0;
		this->idx_write = 0;
		this->overflow = 0;
	}

private:
	core_utils_Buffer<size> buffers[num];  // Array of buffers
	const uint8_t num_buffers = num; // Number of buffers for the queue
	uint8_t idx_write;
	uint8_t idx_read;

	uint8_t inc_write() {
		this->idx_write++;

		if (this->idx_write == this->num_buffers) {
			this->idx_write = 0;
		}
		if (this->idx_write == this->idx_read) {
			this->overflow = 1;
			return 0;
		} else {
			return 1;
		}
	}
	uint8_t inc_read() {
		this->idx_read++;

		if (this->idx_read == this->num_buffers) {
			this->idx_read = 0;
		}
		return 1;
	}
};

#endif /* CORE_UTILS_CORE_UTILS_BUFFERQUEUE_H_ */
