/*
 * twipr_errors.h
 *
 *  Created on: 4 Mar 2023
 *      Author: Dustin Lehmann
 */

#ifndef ERRORS_TWIPR_ERRORS_H_
#define ERRORS_TWIPR_ERRORS_H_

#include "core.h"
#include "robot-control_std.h"
#include "firmware_defs.h"
#include "twipr_messages.h"

typedef struct warning_message_struct_t {
	twipr_error_t error;
	char text[100];
} warning_message_struct_t;

typedef BILBO_Message<warning_message_struct_t, MSG_EVENT, MESSAGE_ID_WARNING> BILBO_Message_Warning;


void twipr_error_handler(uint32_t errorcode);
void twipr_error_handler(uint32_t errorcode, uint8_t *data, uint16_t len);

#endif /* ERRORS_TWIPR_ERRORS_H_ */
