/*
 * usb_socket.c
 *
 *  Created on: Apr 7, 2022
 *      Author: Dustin Lehmann
 */

#include <core_usb.h>
//#include "usbd_cdc_if.h"
//
//extern USBD_HandleTypeDef hUsbDeviceFS;
//
//uint8_t core_usb_Init(core_usb_t *usb_socket) {
//
//	return CORE_OK;
//}
//
//uint8_t core_usb_SendBlocking(core_usb_t *socket, uint8_t *data, uint16_t len,
//		uint16_t timeout) {
//	USBD_CDC_HandleTypeDef *hcdc =
//			(USBD_CDC_HandleTypeDef*) hUsbDeviceFS.pClassData;
//	uint16_t counter = 0;
//	while (hcdc->TxState != 0 && counter < timeout) {
//#ifdef CORE_USE_RTOS
//		osDelay(1);
//#else
//		HAL_Delay(1);
//#endif
//		counter++;
//	}
//	uint8_t ret = CDC_Transmit_FS(data, len);
//	return ret;
//}
