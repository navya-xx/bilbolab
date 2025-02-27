/*
 * core_utils.h
 *
 *  Created on: 20 Apr 2022
 *      Author: lehmann_workstation
 */

#ifndef UTILS_CORE_UTILS_H_
#define UTILS_CORE_UTILS_H_

#include <stdint.h>
#include "config_core.h"
#include "core_error.h"

#define CORE_UTILS_RAW_BUFFER_LENGTH 128

void nop();

typedef enum core_utils_BufferQueueOverflowConfig_t {
	CORE_UTILS_BufferQueueOverflowConfig_ERROR = 0,
	CORE_UTILS_BufferQueueOverflowConfig_HOLD = 1,
	CORE_UTILS_BufferQueueOverflowConfig_OVERWRITE = 2
} core_utils_BufferQueueOverflowConfig_t;

typedef struct core_utils_Buffer_t {
	uint8_t buffer[CORE_UTILS_RAW_BUFFER_LENGTH];
	uint8_t len;
} core_utils_Buffer_t;

/* Message Queues */
typedef struct core_utils_BufferQueue_t {
	uint8_t idx_read;
	uint8_t idx_write;
	core_utils_Buffer_t *buffers;
	core_utils_BufferQueueOverflowConfig_t overflow_config;

	void (*queue_full_callback)(struct core_utils_BufferQueue_t *queue);
	uint8_t overflow;
	uint8_t len;
} core_utils_BufferQueue_t;

uint8_t core_utils_BufferQueue_Init(core_utils_BufferQueue_t *buffer_queue,
		core_utils_Buffer_t *buffers, uint8_t len);

uint8_t core_utils_BufferQueue_Write(core_utils_BufferQueue_t *buffer_queue,
		core_utils_Buffer_t *buffer);

uint8_t core_utils_BufferQueue_WriteArray(
		core_utils_BufferQueue_t *buffer_queue, uint8_t *buffer, uint8_t len);

uint8_t core_utils_BufferQueue_Read(core_utils_BufferQueue_t *buffer_queue,
		core_utils_Buffer_t *buffer);

uint8_t core_utils_BufferQueue_ReadArray(core_utils_BufferQueue_t *buffer_queue,
		uint8_t *buffer);

uint8_t core_utils_BufferQueue_ReadPointer(
		core_utils_BufferQueue_t *buffer_queue, uint8_t **buffer);

int8_t core_utils_BufferQueue_Available(core_utils_BufferQueue_t *buffer_queue);

uint8_t core_utils_BufferQueueClear(core_utils_BufferQueue_t *buffer_queue);

uint8_t core_utils_BufferQueue_RegisterCallback(
		core_utils_BufferQueue_t *buffer_queue,
		void (*queue_full_callback)(struct core_utils_BufferQueue_t *queue));


/* Private Functions */
uint8_t _core_utils_BufferQueue_IncWrite(core_utils_BufferQueue_t *buffer_queue);
uint8_t _core_utils_BufferQueue_IncRead(core_utils_BufferQueue_t *buffer_queue);

/* Callback Functions */
typedef struct core_utils_Callback_t {
	void (*callback)(void *argument, void* params);
	void *params;
	uint8_t registered;
} core_utils_Callback_t;


/* COBS */

uint8_t cobsEncode(uint8_t *data, uint8_t length, uint8_t *buffer);
uint8_t cobsDecode(uint8_t *buffer, uint8_t length, uint8_t *data);


/* Byte manipulation */

float bytearray_to_float(uint8_t* bytearray);


#endif /* UTILS_CORE_UTILS_H_ */
