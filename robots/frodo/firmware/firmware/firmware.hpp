/*
 * firmware.hpp
 *
 *  Created on: Feb 13, 2023
 *      Author: lehmann_workstation
 */

#ifndef FIRMWARE_HPP_
#define FIRMWARE_HPP_


#include <stdio.h>

#include "frodo_logging.h"
#include "frodo_drive.h"
#include "twipr_communication.h"
#include "robot-control_std.h"
#include "twipr_errors.h"
#include "firmware_defs.h"
#include "io.h"

#include "encoder.h"
#include "frodo_motors.h"

typedef BILBO_Message<frodo_sample_t, MSG_STREAM, FRODO_MESSAGE_ID_SAMPLE_STREAM> frodo_message_sample_stream_t;

class FRODO_Firmware {
public:
	FRODO_Firmware();

	void init();
	void start();

	void helperTask();

	void controlTask();


	void sendData();

	frodo_general_sample_t getSample();

	FRODO_Drive drive;
	TWIPR_CommunicationManager comm;
	FRODO_Logging logging;

	frodo_sample_t data = {0};

	elapsedMillis help_timer;

	uint32_t tick = 0;

private:


};


void start_firmware_task(void*);
void start_firmare_control_task(void*);
#endif /* FIRMWARE_HPP_ */
