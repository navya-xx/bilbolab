/*
 * firmware.hpp
 *
 *  Created on: Feb 13, 2023
 *      Author: lehmann_workstation
 */

#ifndef FIRMWARE_HPP_
#define FIRMWARE_HPP_

#include "twipr_communication.h"
#include "twipr_drive_can.h"
#include "twipr_control.h"
#include "robot-control_std.h"
#include "twipr_estimation.h"
#include "twipr_errors.h"
#include "twipr_logging.h"
#include "firmware_defs.h"
#include "twipr_safety.h"
#include "twipr_sequencer.h"
#include "io.h"


typedef struct test_struct_t {
	float a;
	uint8_t b;
}test_struct_t;

class TWIPR_Firmware {

public:
	TWIPR_Firmware();
	HAL_StatusTypeDef init();
	HAL_StatusTypeDef start();
	void step();

	void helperTask();
	void controlTask();
	void controlTaskStep();

	twipr_logging_general_t getSample();

	void errorHandler(twipr_error_t error);


	twipr_debug_sample_t getDebugSample();

	twipr_firmware_state_t firmware_state = TWIPR_FIRMWARE_STATE_RESET;
	twipr_error_t error = TWIPR_ERROR_NONE;

	twipr_firmware_revision_t revision = {.major = TWIPR_FIRMWARE_REVISION_MAJOR,
										  .minor = TWIPR_FIRMWARE_REVISION_MINOR};
	uint32_t tick = 0;

	TWIPR_Drive_CAN drive;


	TWIPR_CommunicationManager comm;
	TWIPR_ControlManager control;
	TWIPR_Sequencer sequencer;
	TWIPR_Estimation estimation;
	TWIPR_Supervisor supervisor;
	TWIPR_Sensors sensors;
	TWIPR_Logging logging;

	uint8_t debug(uint8_t input);

	twipr_debug_sample_t debugData;

private:

	twipr_logging_buffer_status_t sample_buffer_state;

	elapsedMillis timer_control_mode_led;

	void setControlModeLed();
};

void start_firmware_task(void *argument);
void start_firmware_control_task(void *argument);

#endif /* FIRMWARE_HPP_ */
