/*
 * core_utils_BufferQueue.cpp
 *
 *  Created on: Jul 7, 2022
 *      Author: Dustin Lehmann
 */

#include "core_utils_BufferQueue.h"

//template<int num>
//core_utils_BufferQueue<num>::core_utils_BufferQueue() {
//	this->idx_read = 0;
//	this->idx_write = 0;
//	this->overflow = 0;
//}

//template<int num>
//int8_t core_utils_BufferQueue<num>::available() {
//	if (this->overflow) {
//		return -1;
//	}
//	int8_t available = this->idx_write - this->idx_read;
//	if (available < 0) {
//		available += this->num_buffers;
//	}
//	return available;
//}

//template<int num>
//uint8_t core_utils_BufferQueue<num>::write(core_utils_Buffer *buffer) {
//
//	for (int i = 0; i < buffer->len; i++) {
//		this->buffers[this->idx_write].buffer[i] = buffer->buffer[i];
//	}
//
//	this->buffers[this->idx_write].len = buffer->len;
//	return this->inc_write();
//}

//template<int num>
//uint8_t core_utils_BufferQueue<num>::write(uint8_t *buffer, uint16_t len) {
//	for (int i = 0; i < len; i++) {
//		this->buffers[this->idx_write].buffer[i] = buffer[i];
//	}
//	return this->inc_write();
//}

//template<int num>
//uint8_t core_utils_BufferQueue<num>::read(core_utils_Buffer *buffer) {
//	if (this->available() < 1) {
//		return 0;
//	}
//	*buffer = this->buffers[this->idx_read];
//	this->inc_read();
//	return 1;
//}
//
//template<int num>
//uint8_t core_utils_BufferQueue<num>::read(uint8_t *buffer) {
//	if (this->available() < 1) {
//		return 0;
//	}
//	for (int i = 0; i < this->buffers[this->idx_read].len; i++) {
//		buffer[i] = this->buffers[this->idx_read].buffer[i];
//	}
//
//	uint8_t len = this->buffers[this->idx_read].len;
//	this->inc_read();
//
//	return len;
//}
//
//template<int num>
//uint8_t core_utils_BufferQueue<num>::read(uint8_t **buffer) {
//	if (this->available() < 1) {
//		return 0;
//	}
//	*buffer = &this->buffers[this->idx_read].buffer[0];
//
//	uint8_t len = this->buffers[this->idx_read].len;
//	this->inc_read();
//	return len;
//}

//template<int num>
//uint8_t core_utils_BufferQueue<num>::inc_write() {
//	this->idx_write++;
//
//	if (this->idx_write == this->num_buffers) {
//		this->idx_write = 0;
//	}
//	if (this->idx_write == this->idx_read) {
//		this->overflow = 1;
//		return 0;
//	} else {
//		return 1;
//	}
//}

//template<int num>
//uint8_t core_utils_BufferQueue<num>::inc_read() {
//	this->idx_read++;
//
//	if (this->idx_read == this->num_buffers) {
//		this->idx_read = 0;
//	}
//	return 1;
//}

//template<int num>
//void core_utils_BufferQueue<num>::clear() {
//	this->idx_read = 0;
//	this->idx_write = 0;
//	this->overflow = 0;
//}
