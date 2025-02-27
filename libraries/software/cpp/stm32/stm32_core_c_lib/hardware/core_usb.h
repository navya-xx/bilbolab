/*
 * usb_socket.h
 *
 *  Created on: Apr 7, 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_INC_CORE_USB_H_
#define CORE_INC_CORE_USB_H_

//#include "usbd_cdc_if.h"


#ifdef CORE_USE_RTOS
//#include <cmsis_os2.h>
#endif

#include "config_core.h"


//
//#define CORE_USB_RX_BUFFER_LENGTH 255
//
//typedef struct {
//	uint8_t rx_buf[CORE_USB_RX_BUFFER_LENGTH];
//	USBD_CDC_HandleTypeDef* usb;
//} core_usb_t;
//
//uint8_t core_usb_Init(core_usb_t *usb_socket);
//
///* Sending */
//uint8_t core_usb_SendBlocking(core_usb_t *socket, uint8_t *data, uint16_t len,
//		uint16_t timeout);
//
//uint8_t core_usb_DataAvailable();
//uint8_t core_usb_ReadData();

#endif /* CORE_INC_CORE_USB_H_ */
