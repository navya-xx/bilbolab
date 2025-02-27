/*
 * twipr_safety.h
 *
 *  Created on: Feb 22, 2023
 *      Author: lehmann_workstation
 */

#ifndef SAFETY_TWIPR_SAFETY_H_
#define SAFETY_TWIPR_SAFETY_H_

#include "core.h"
#include "twipr_errors.h"
//#include "twipr_drive.h"
#include "twipr_drive_can.h"
#include "twipr_control.h"
#include "twipr_communication.h"

typedef struct twipr_supervisor_stuck_config_t {
	float max_velocity_error = 0.1;
	float max_pitch_angle_deviation = 0.05;
	int stuck_duration = 50;
} twipr_supervisor_stuck_config_t;

typedef struct twipr_supervisor_stuck_data_t {
	bool is_stuck = false;
	float last_velocity_error = 0;
	float last_pitch_angle = 0;
	float error_count = 0;
} twipr_supervisor_stuck_data_t;

typedef struct twipr_supervisor_controller_config_t {
	float max_forward_pid_integrator = 0.2;
	float max_turn_pid_integrator = 0.2;
} twipr_supervisor_controller_config_t;

typedef struct twipr_supervisor_config_t {
	TWIPR_Estimation *estimation;
	TWIPR_Drive_CAN *drive;
	TWIPR_ControlManager *control;
	TWIPR_CommunicationManager *communication;
	core_hardware_Button *off_button;
	float max_wheel_speed;
	twipr_supervisor_stuck_config_t stuck_config;
	twipr_supervisor_controller_config_t controller_config;
} twipr_supervisor_config_t;


class TWIPR_Supervisor {
public:
	TWIPR_Supervisor();

	void init(twipr_supervisor_config_t config);
	void start();

	twipr_error_t check();

	void task();

	twipr_supervisor_config_t config;

private:

	twipr_error_t error = TWIPR_ERROR_NONE;
	void setError(twipr_error_t error);

	uint32_t lastDriveTick = 0;
	twipr_supervisor_error_t last_errors[10];

	twipr_supervisor_error_t checkStuck();
	twipr_supervisor_stuck_data_t stuck_data;

	twipr_supervisor_error_t checkControllers();

	twipr_supervisor_error_t checkMotors();

	twipr_supervisor_error_t checkMotorSpeed();

	twipr_supervisor_error_t checkButton();

	void sendWarning(twipr_supervisor_error_t id, twipr_error_t error,
			const char *message, uint8_t len);

};

void startTwiprSupervisorTask(void *args);

#endif /* SAFETY_TWIPR_SAFETY_H_ */
