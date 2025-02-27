/*
 * core_utils.h
 *
 *  Created on: Jul 7, 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_UTILS_CORE_UTILS_H_
#define CORE_UTILS_CORE_UTILS_H_

#include "cobs.h"
#include "core_bytes.h"
#include "core_errors.h"
#include "core_math.h"
#include "core_utils_gpio.h"
#include "core_utils_BufferQueue.h"
#include "core_utils_Callback.h"
#include "core_utils_RingBuffer.h"
#include "core_utils_functionpointer.h"
#include "core_utils_registermap.h"
#include "elapsedMillis.h"


inline void nop(){

}

inline void delay(uint32_t msec){
#if CORE_CONFIG_USE_RTOS

	osKernelState_t state = osKernelGetState();
	if (state == osKernelRunning){
		osDelay(msec);
	} else {
		HAL_Delay(msec);
	}

#else
	HAL_Delay(msec);
#endif
}



#endif /* CORE_UTILS_CORE_UTILS_H_ */
