/*
 * twipr_errors.cpp
 *
 *  Created on: 6 Mar 2023
 *      Author: lehmann_workstation
 */


#include "twipr_errors.h"

void twipr_error_handler(uint32_t errorcode) {

	// Turn on the LED2

	// if the error code starts with 0x00 then it's severe and should result in a firmware stop
	if (errorcode >> 24 == 0x00) {
		// Try to suspend all tasks
		vTaskSuspendAll();
		while (true) {
			uint8_t id1 = errorcode >> 8 & 0xFF;
			uint8_t id2 = errorcode & 0xFF;

			for (int i = 0; i < id1; i++) {
				rc_status_led_2.on();
				HAL_Delay(150);
				rc_status_led_2.off();
				HAL_Delay(150);
			}
			delay(750);
			for (int i = 0; i < id2; i++) {
				rc_status_led_2.on();
				HAL_Delay(150);
				rc_status_led_2.off();
				HAL_Delay(150);
			}
			HAL_Delay(1500);
		}
	}
}

void twipr_error_handler(uint32_t errorcode, uint8_t *data, uint16_t len) {

}

