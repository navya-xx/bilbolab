/*
 * bytes.cpp
 *
 *  Created on: 7 Jul 2022
 *      Author: Dustin Lehmann
 */

#include "core_bytes.h"

float bytearray_to_float(uint8_t *bytearray) {
	uint32_t temp = 0;
	temp = ((bytearray[3] << 24) | (bytearray[2] << 16) | (bytearray[1] << 8)
			| bytearray[0]);
	return *((float*) &temp);
}

uint16_t uint8_to_uint16(uint8_t byte1, uint8_t byte2) {
	uint16_t out = byte1 << 8 | byte2;
	return out;
}

uint16_t bytearray_to_uint16(uint8_t *bytearray) {
	uint16_t out = bytearray[1] << 8 | bytearray[0];
	return out;
}

int16_t bytearray_to_int16(uint8_t *bytearray) {
	int16_t out = bytearray[1] << 8 | bytearray[0];
	return out;
}

//int16_t bytearray_to_int16(uint8_t *bytearray) {
//	int16_t out = bytearray[0] << 8 | bytearray[1];
//	return out;
//}

uint32_t bytearray_to_uint32(uint8_t *bytearray) {
	uint32_t temp = 0;
	temp = ((bytearray[3] << 24) | (bytearray[2] << 16) | (bytearray[1] << 8)
			| bytearray[0]);
	return temp;
}

int32_t bytearray_to_int32(uint8_t *bytearray) {
	int32_t temp = 0;
	temp = ((bytearray[3] << 24) | (bytearray[2] << 16) | (bytearray[1] << 8)
			| bytearray[0]);
	return temp;
}


void float_to_bytearray(float value, uint8_t* bytearray) {
    uint32_t l = *(uint32_t*) &value;

    bytearray[0] = l & 0x00FF;
    bytearray[1] = (l >> 8) & 0x00FF;
    bytearray[2] = (l >> 16) & 0x00FF;
    bytearray[3] = l >> 24;
}

void int32_to_bytearray(int32_t value, uint8_t* bytearray){
    // Ensure the bytearray pointer is not null

    // Break the int32_t value into 4 bytes and store them in the bytearray (little-endian order)
    bytearray[0] = value & 0xFF;         // Least significant byte
    bytearray[1] = (value >> 8) & 0xFF;
    bytearray[2] = (value >> 16) & 0xFF;
    bytearray[3] = (value >> 24) & 0xFF; // Most significant byte
}

void uint32_to_bytearray(uint32_t value, uint8_t* bytearray){
    // Break the int32_t value into 4 bytes and store them in the bytearray (little-endian order)
    bytearray[0] = value & 0xFF;         // Least significant byte
    bytearray[1] = (value >> 8) & 0xFF;
    bytearray[2] = (value >> 16) & 0xFF;
    bytearray[3] = (value >> 24) & 0xFF; // Most significant byte
}

void uint16_to_bytearray(uint16_t value, uint8_t* bytearray){
    bytearray[0] = value & 0xFF;         // Least significant byte
    bytearray[1] = (value >> 8) & 0xFF;  // Most significant byte
}

void int16_to_bytearray(int16_t value, uint8_t* bytearray){
    bytearray[0] = value & 0xFF;         // Least significant byte
    bytearray[1] = (value >> 8) & 0xFF;  // Most significant byte
}

void uint32_to_bytearray(uint16_t value, uint8_t* bytearray){
    bytearray[0] = value & 0xFF;         // Least significant byte
    bytearray[1] = (value >> 8) & 0xFF;  // Most significant byte
}
