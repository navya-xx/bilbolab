/*
 * cobs.h
 *
 *  Created on: 7 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_UTILS_COBS_H_
#define CORE_UTILS_COBS_H_

#include "stdint.h"

uint8_t cobsEncode(uint8_t *data_in, uint8_t length, uint8_t *data_out);
uint8_t cobsDecode(uint8_t *buffer, uint8_t length, uint8_t *data);
uint8_t cobsDecodeInPlace(uint8_t *buffer, uint8_t length);

#endif /* CORE_UTILS_COBS_H_ */
