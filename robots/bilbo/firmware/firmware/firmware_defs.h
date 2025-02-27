/*
 * firmware_defs.h
 *
 *  Created on: 16 Mar 2023
 *      Author: lehmann_workstation
 */

#ifndef FIRMWARE_DEFS_H_
#define FIRMWARE_DEFS_H_

#include "core.h"
#include "firmware_settings.h"


#define TWIPR_REGISTER_MAP_GENERAL 0x01

// Register Maps and Messages on the CM4
#define CM4_STANDARD_REGISTER_MAP 0x01

// Messages
#define TWIPR_MESSAGE_EVENT_WARNING 0x0301


// Register Addresses
#define REG_ADDRESS_R_FIRMWARE_STATE 0x01
#define REG_ADDRESS_R_FIRMWARE_TICK 0x02
#define REG_ADDRESS_R_FIRMWARE_REVISION 0x03
#define REG_ADDRESS_F_FIRMWARE_DEBUGFUNCTION 0x04
#define REG_ADDRESS_F_FIRMWARE_BEEP 0x05
#define REG_ADDRESS_R_BOARD_REVISION 0x06

#define REG_ADDRESS_F_EXTERNAL_LED 0x07
#define REG_ADDRESS_RW_DEBUG_1 0x08


#define REG_ADDRESS_R_CONTROL_MODE 0x10
#define REG_ADDRESS_F_CONTROL_SET_MODE 0x11
#define REG_ADDRESS_F_CONTROL_SET_K 0x12
#define REG_ADDRESS_F_CONTROL_SET_FORWARD_PID 0x13
#define REG_ADDRESS_F_CONTROL_SET_TURN_PID 0x14
#define REG_ADDRESS_F_CONTROL_SET_DIRECT_INPUT 0x15
#define REG_ADDRESS_F_CONTROL_SET_BALANCING_INPUT 0x16
#define REG_ADDRESS_F_CONTROL_SET_SPEED_INPUT 0x17
#define REG_ADDRESS_F_CONTROL_GET_CONFIGURATION 0x18

#define REG_ADDRESS_RW_MAX_WHEEL_SPEED 0x20


#define REG_ADDRESS_F_SEQUENCE_LOAD 0x21
#define REG_ADDRESS_F_SEQUENCE_START 0x22
#define REG_ADDRESS_F_SEQUENCE_STOP 0x23


// ------------------------------------------------------------------------------------------------ //
typedef struct twipr_firmware_revision_t {
	uint8_t major;
	uint8_t minor;
}twipr_firmware_revision_t;

// ------------------------------------------------------------------------------------------------ //
typedef enum twipr_error_t {
	TWIPR_ERROR_NONE = 0,
	TWIPR_ERROR_CRITICAL = 1,
	TWIPR_ERROR_WARNING = 2,
} twipr_error_t;

typedef enum twipr_supervisor_error_t {
	TWIPR_SUPERVISOR_NONE = 0,
	TWIPR_SUPERVISOR_STUCK = 1,
	TWIPR_SUPERVISOR_WHEEL_SPEED = 2,
	TWIPR_SUPERVISOR_MANUAL_STOP = 3,
	TWIPR_SUPERVISOR_MOTOR_TIMEOUT = 4,
	TWIPR_FIRMWARE_ERROR_RACE_CONDITION = 5,
	TWIPR_SUPERVISOR_ERROR_INTEGRATOR_OVERRUN = 6,
	TWIPR_SUPERVISOR_MOTOR_RACECONDITION_RESETS = 7
} twipr_supervisor_error_t;

typedef enum twipr_firmware_state_t {
	TWIPR_FIRMWARE_STATE_ERROR = -1,
	TWIPR_FIRMWARE_STATE_IDLE = 0,
	TWIPR_FIRMWARE_STATE_RUNNING = 1,
	TWIPR_FIRMWARE_STATE_RESET = 2,
} twipr_firmware_state_t;

typedef struct twipr_logging_general_t {
	uint32_t tick;
	twipr_firmware_state_t state;
	twipr_error_t error;
} twipr_logging_general_t;

#define TWIPR_FIRMWARE_SAMPLE_BUFFER_SIZE (uint16_t) (TWIPR_FIRMWARE_SAMPLE_BUFFER_TIME * 1000 / TWIPR_CONTROL_TS_MS)
#define TWIPR_SEQUENCE_BUFFER_SIZE (uint32_t) (TWIPR_SEQUENCE_TIME * 1000/TWIPR_CONTROL_TS_MS)
#define TWIPR_CONTROL_TS_MS (uint32_t) (1000.0 / TWIPR_CONTROL_TASK_FREQ)


extern DMA_HandleTypeDef hdma_memtomem_dma2_stream0;
#define TWIPR_FIRMWARE_SAMPLE_DMA_STREAM &hdma_memtomem_dma2_stream0

#endif /* FIRMWARE_DEFS_H_ */

