/*
 * elapsedMillis.cpp
 *
 *  Created on: Jul 12, 2022
 *      Author: Dustin Lehmann
 */

#include "../core_includes.h"

#include "elapsedMillis.h"

uint32_t millis() {
#if CORE_CONFIG_USE_RTOS
	return osKernelGetTickCount();
#else
	return HAL_GetTick();
#endif
}



