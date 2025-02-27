/*
 * core_coremessages.c
 *
 *  Created on: Jun 27, 2022
 *      Author: Dustin Lehmann
 */

#include "core_coremessages.h"

void core_msg_rxHandler(core_comm_Message_t *msg) {
	switch (msg->cmd) {
	case CORE_MSG_TYPE_WRITE: {
		core_msg_write_rxHandler(msg);
		break;
	}
	}
}

