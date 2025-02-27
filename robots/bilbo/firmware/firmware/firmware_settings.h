/*
 * firmware_setting.h
 *
 *  Created on: 3 Mar 2023
 *      Author: lehmann_workstation
 */

#ifndef FIRMWARE_SETTINGS_H_
#define FIRMWARE_SETTINGS_H_

/* USER SETTINGS */
// REVISION
#define TWIPR_FIRMWARE_REVISION_MAJOR 0x02
#define TWIPR_FIRMWARE_REVISION_MINOR 0x02

// FIRMWARE MODES
#define TWIPR_FIRMWARE_USE_MOTORS 1

// Main Task Frequency
#define TWIPR_CONTROL_TASK_FREQ 100

// Control
#define TWIPR_CONTROL_MAX_TORQUE 0.3
#define TWIPR_SAFETY_MAX_WHEEL_SPEED 75

// Control - Trajectories
#define TWIPR_SEQUENCE_TIME 60 // seconds

// Logging
#define TWIPR_FIRMWARE_SAMPLE_BUFFER_TIME 0.1 // seconds


#endif /* FIRMWARE_SETTINGS_H_ */
