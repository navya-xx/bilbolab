/*
 * cobs.cpp
 *
 *  Created on: 7 Jul 2022
 *      Author: Dustin Lehmann
 */

#include "cobs.h"


uint8_t cobsDecodeBuffer[256];

/** COBS encode data to buffer
	@param data Pointer to input data to encode
	@param length Number of bytes to encode
	@param buffer Pointer to encoded output buffer
	@return Encoded buffer length in bytes
	@note Does not output delimiter byte
*/
uint8_t cobsEncode(uint8_t *data_in, uint8_t length, uint8_t *data_out)
{

	uint8_t *encode = data_out; // Encoded byte pointer
	uint8_t *codep = encode++; // Output code pointer
	uint8_t code = 1; // Code value

	for (const uint8_t *byte = (const uint8_t *)data_in; length--; ++byte)
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

	return (uint8_t)(encode - data_out);
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



uint8_t cobsDecodeInPlace(uint8_t *buffer, uint8_t length)
{
	uint8_t decode_len = cobsDecode(buffer, length, cobsDecodeBuffer);

	for (int i = 0; i<decode_len; i++){
		buffer[i] = cobsDecodeBuffer[i];
	}

	return decode_len;
}
