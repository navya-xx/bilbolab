/*
 * core_error.h
 *
 *  Created on: 19 Apr 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_ERROR_H_
#define CORE_ERROR_H_

#include <stdint.h>


#define CORE_ERROR_HARDWARE_INIT 0x10




void core_ErrorHandler(uint8_t error);

#endif /* CORE_ERROR_H_ */
