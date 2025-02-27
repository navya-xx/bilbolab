/*
 * core_config.h
 *
 *  Created on: Jul 6, 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_CORE_DEFAULT_CONFIG_H_
#define CORE_CORE_DEFAULT_CONFIG_H_


#ifdef CORE_CONFIG_OVERWRITE
#include <core_config.h>
#else
/* =============================== BOARD DEFINITION ================================== */

/* --- MCU ------------------------------------------------ */

#define CORE_CONFIG_MCU_STM32H7
//#define CORE_CONFIG_MCU_STM32F4


/* --- BOARD ---------------------------------------------- */


/* =============================== FIRMWARE DEFINITIONS ================================ */
/* --- RTOS ------------------------------------------------ */
#define CORE_CONFIG_USE_RTOS 1



/* =============================== INTERFACES ========================================== */
/* --- UART ------------------------------------------------ */
#define CORE_CONFIG_USE_UART 1
/* --- SPI ------------------------------------------------- */
#define CORE_CONFIG_USE_SPI 1
/* --- I2C ------------------------------------------------- */
#define CORE_CONFIG_USE_I2C 1
/* --- USB ------------------------------------------------- */
#define CORE_CONFIG_USE_USB 0

#endif




#define CORE_CONFIG_MSG_HEADER 0x55
#define CORE_CONFIG_MSG_FOOTER



#define CORE_CONFIG_MAX_MSG_LENGTH 128
#define CORE_CONFIG_MSG_QUEUE_SIZE 10
#define CORE_CONFIG_MAX_UARTS 5



#endif

/* CORE_CORE_DEFAULT_CONFIG_H_ */
