/*
 * core_utils.c
 *
 *  Created on: 20 Apr 2022
 *      Author: lehmann_workstation
 */

#include "core_utils.h"

void nop() {

}

uint8_t core_utils_BufferQueue_Init(core_utils_BufferQueue_t *buffer_queue,
		core_utils_Buffer_t *buffers, uint8_t len) {
	buffer_queue->buffers = buffers;
	buffer_queue->len = len;

	return CORE_OK;
}

int8_t core_utils_BufferQueue_Available(core_utils_BufferQueue_t *buffer_queue) {
	if (buffer_queue->overflow) {
		return 0;
	}
	int8_t available = buffer_queue->idx_write - buffer_queue->idx_read;
	if (available < 0) {
		available += buffer_queue->len;
	}
	return available;
}

uint8_t core_utils_BufferQueue_Write(core_utils_BufferQueue_t *buffer_queue,
		core_utils_Buffer_t *buffer) {
	buffer_queue->buffers[buffer_queue->idx_write] = *buffer;

	return _core_utils_BufferQueue_IncWrite(buffer_queue);
}

uint8_t core_utils_BufferQueue_WriteArray(
		core_utils_BufferQueue_t *buffer_queue, uint8_t *buffer, uint8_t len) {
	if (buffer_queue->overflow) {
		return 0;
	}

	for (int i = 0; i < len; i++) {
		buffer_queue->buffers[buffer_queue->idx_write].buffer[i] = buffer[i];
	}

	buffer_queue->buffers[buffer_queue->idx_write].len = len;

	return _core_utils_BufferQueue_IncWrite(buffer_queue);
}

uint8_t _core_utils_BufferQueue_IncWrite(core_utils_BufferQueue_t *buffer_queue) {
	buffer_queue->idx_write++;

	if (buffer_queue->idx_write == buffer_queue->len) {
		buffer_queue->idx_write = 0;
	}

	if (buffer_queue->idx_write == buffer_queue->idx_read) {
		buffer_queue->overflow = 1;
		return 0;
	}
	return CORE_OK;
}

uint8_t core_utils_BufferQueue_Read(core_utils_BufferQueue_t *buffer_queue,
		core_utils_Buffer_t *buffer) {
	if (core_utils_BufferQueue_Available(buffer_queue) == 0
			|| core_utils_BufferQueue_Available(buffer_queue) == -1) {
		return 0;
	}

	*buffer = buffer_queue->buffers[buffer_queue->idx_read];
	_core_utils_BufferQueue_IncRead(buffer_queue);
	return CORE_OK;
}

uint8_t core_utils_BufferQueue_ReadArray(core_utils_BufferQueue_t *buffer_queue,
		uint8_t *buffer) {

	if (core_utils_BufferQueue_Available(buffer_queue) == 0
			|| core_utils_BufferQueue_Available(buffer_queue) == -1) {
		return 0;
	}

	for (int i = 0; i < buffer_queue->buffers[buffer_queue->idx_read].len;
			i++) {
		buffer[i] = buffer_queue->buffers[buffer_queue->idx_read].buffer[i];
	}

	uint8_t len = buffer_queue->buffers[buffer_queue->idx_read].len;
	_core_utils_BufferQueue_IncRead(buffer_queue);

	return len;
}

uint8_t core_utils_BufferQueue_ReadPointer(
		core_utils_BufferQueue_t *buffer_queue, uint8_t **buffer) {
	if (core_utils_BufferQueue_Available(buffer_queue) == 0
			|| core_utils_BufferQueue_Available(buffer_queue) == -1) {
		return 0;
	}

	*buffer = &buffer_queue->buffers[buffer_queue->idx_read].buffer[0];

	uint8_t len = buffer_queue->buffers[buffer_queue->idx_read].len;
	_core_utils_BufferQueue_IncRead(buffer_queue);

	return len;
}

uint8_t _core_utils_BufferQueue_IncRead(core_utils_BufferQueue_t *buffer_queue) {
	buffer_queue->idx_read++;
	if (buffer_queue->idx_read == buffer_queue->len) {
		buffer_queue->idx_read = 0;
	}

	buffer_queue->overflow = 0;

	return CORE_OK;
}

uint8_t core_utils_BufferQueueClear(core_utils_BufferQueue_t *buffer_queue) {
	buffer_queue->idx_read = 0;
	buffer_queue->idx_write = 0;
	buffer_queue->overflow = 0;

	return CORE_OK;
}

uint8_t core_utils_BufferQueue_RegisterCallback(
		core_utils_BufferQueue_t *buffer_queue,
		void (*queue_full_callback)(struct core_utils_BufferQueue_t *queue)) {

	buffer_queue->queue_full_callback = queue_full_callback;
	return CORE_OK;
}


/** COBS encode data to buffer
	@param data Pointer to input data to encode
	@param length Number of bytes to encode
	@param buffer Pointer to encoded output buffer
	@return Encoded buffer length in bytes
	@note Does not output delimiter byte
*/
uint8_t cobsEncode(uint8_t *data, uint8_t length, uint8_t *buffer)
{

	uint8_t *encode = buffer; // Encoded byte pointer
	uint8_t *codep = encode++; // Output code pointer
	uint8_t code = 1; // Code value

	for (const uint8_t *byte = (const uint8_t *)data; length--; ++byte)
	{
		if (*byte) // Byte not zero, write it
			*encode++ = *byte, ++code;

		if (!*byte || code == 0xff) // Input is zero or block completed, restart
		{
			*codep = code, code = 1, codep = encode;
			if (!*byte || length)
				++encode;
		}
	}
	*codep = code; // Write final code value

	return (uint8_t)(encode - buffer);
}

/** COBS decode data from buffer
	@param buffer Pointer to encoded input bytes
	@param length Number of bytes to decode
	@param data Pointer to decoded output data
	@return Number of bytes successfully decoded
	@note Stops decoding if delimiter byte is found
*/
uint8_t cobsDecode(uint8_t *buffer, uint8_t length, uint8_t *data)
{

	const uint8_t *byte = buffer; // Encoded input byte pointer
	uint8_t *decode = (uint8_t *)data; // Decoded output byte pointer

	for (uint8_t code = 0xff, block = 0; byte < buffer + length; --block)
	{
		if (block) // Decode block byte
			*decode++ = *byte++;
		else
		{
			if (code != 0xff) // Encoded zero, write it
				*decode++ = 0;
			block = code = *byte++; // Next block length
			if (!code) // Delimiter code found
				break;
		}
	}

	return (uint8_t)(decode - (uint8_t *)data);
}






float bytearray_to_float(uint8_t* bytearray){
	uint32_t temp = 0;
    temp = ((bytearray[3] << 24) |
            (bytearray[2] << 16) |
            (bytearray[1] <<  8) |
			bytearray[0]);
    return *((float *) &temp);
}
