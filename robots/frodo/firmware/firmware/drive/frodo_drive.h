/*
 * speed-control.h
 *
 *  Created on: May 17, 2024
 *      Author: Jarne Bärmann
 */

#ifndef SPEED_CONTROL_H_
#define SPEED_CONTROL_H_

#include "encoder.h"
#include "frodo_motors.h"

#define NUM_ACTUATORS 2
#define VELOCITY_AT_05 103	/* Velocity for Turn Speed at input 0.5 [mm/s] */
#define D_PHI 125 			/* Diameter */
#define TURN_SCALE 5/4		/* Scalar for Turn Time */


typedef struct frodo_drive_config_t {
	GPIO_TypeDef *motor_left_dir_port;
	uint16_t motor_left_dir_pin;
	TIM_HandleTypeDef *motor_left_htim;
	uint32_t motor_left_timer_channel;
	TIM_HandleTypeDef *motor_left_encoder_htim;
	int8_t motor_left_direction;
	float motor_left_velocity_scale;

	GPIO_TypeDef *motor_right_dir_port;
	uint16_t motor_right_dir_pin;
	TIM_HandleTypeDef *motor_right_htim;
	uint32_t motor_right_timer_channel;
	TIM_HandleTypeDef *motor_right_encoder_htim;
	int8_t motor_right_direction;
	float motor_right_velocity_scale;

	int update_time_ms;

} frodo_drive_config_t;

typedef struct speed_control_config_t {
	int enc_scan_time_ms;
	float enc_velocity_scalor;
} speed_control_config_t;

typedef struct motor_input_t {
	float left;
	float right;
} motor_input_t;

typedef struct motor_rpm_t {
	float left;
	float right;
} motor_rpm_t;

typedef struct motor_speed_t {
	float left;
	float right;
} motor_speed_t;


typedef struct frodo_drive_sample_t {
	motor_speed_t speed;
	motor_speed_t goal_speed;
	motor_rpm_t rpm;
} frodo_drive_sample_t;


class FRODO_Drive {
public:

	FRODO_Drive();
	void init(frodo_drive_config_t config);
	void start();

	void update();
	void setSpeed(motor_input_t input);


	frodo_drive_sample_t getSample();

	motor_speed_t getSpeed();
	motor_rpm_t getRPM();
	motor_speed_t getGoalSpeed();

private:

	frodo_drive_config_t config;
	Motor motor_left;
	Motor motor_right;
	Encoder encoder_left;
	Encoder encoder_right;
};

#endif /* SPEED_CONTROL_H_ */
