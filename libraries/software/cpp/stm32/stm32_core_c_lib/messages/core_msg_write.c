/*
 * core_msg_write.c
 *
 *  Created on: Jun 27, 2022
 *      Author: Dustin Lehmann
 */

#include "core_msg_write.h"

void core_msg_write_rxHandler(core_comm_Message_t *msg) {
	switch (msg->msg) {
	case MSG_CORE_WRITE_Led_ID: {
		core_msg_core_write_led_rxHandler(msg);
		break;
	}
	}
}

/*
 *
 *  Payload
 * 	BYTE	|	NAME				|	DATATYPE		|	DESCRIPTION					|
 * 	0		|	LED_NUM				|	uint8			|	1 = LED1, 2 = LED2			|
 * 	1		|	LED_STATE			|	int8			|	0 = off, 1 = on, -1 = toggle|
 */
void core_msg_core_write_led_rxHandler(core_comm_Message_t *msg) {
	if (!(msg->data_len == MSG_CORE_WRITE_Led_LEN)) {
		return;
	}

//	uint8_t led_num = msg->data[0];
//	int8_t led_state = (int8_t) msg->data[1];
}

