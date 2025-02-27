/*
 * bytes.h
 *
 *  Created on: 7 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_UTILS_CORE_BYTES_H_
#define CORE_UTILS_CORE_BYTES_H_

#include "stdint.h"

#define bitRead(value, bit) (((value) >> (bit)) & 0x01)
#define bitSet(value, bit) ((value) |= (1UL << (bit)))
#define bitClear(value, bit) ((value) &= ~(1UL << (bit)))
#define bitWrite(value, bit, bitvalue) ((bitvalue) ? bitSet(value, bit) : bitClear(value, bit))

#define lowByte(w) ((w) & 0xff)
#define highByte(w) ((w) >> 8)


typedef union {
	uint8_t u8[4];
	uint16_t u16[2];
	uint32_t u32;
} bytesFields;

float bytearray_to_float(uint8_t* bytearray);
uint16_t bytearray_to_uint16(uint8_t* bytearray);
int16_t bytearray_to_int16(uint8_t* bytearray);
uint32_t bytearray_to_uint32(uint8_t* bytearray);
int32_t bytearray_to_int32(uint8_t *bytearray);

void float_to_bytearray(float value, uint8_t* bytearray);
uint16_t uint8_to_uint16(uint8_t byte1, uint8_t byte2);
void int32_to_bytearray(int32_t value, uint8_t* bytearray);
void uint16_to_bytearray(uint16_t value, uint8_t* bytearray);
void int16_to_bytearray(int16_t value, uint8_t* bytearray);
void uint32_to_bytearray(uint32_t value, uint8_t* bytearray);


#endif /* CORE_UTILS_CORE_BYTES_H_ */
