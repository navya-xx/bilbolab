/*
 * motors.h
 *
 *  Created on: May 7, 2024
 *      Author: Dustin Lehmann
 */

#ifndef MOTORS_H_
#define MOTORS_H_

#include "stm32h7xx_hal.h"

class FRODO_Drive;

#define MAX_ROT_SPEED 151 /* [1/min] */

typedef struct motor_config_t {
	TIM_HandleTypeDef* pwm_timer;
	uint32_t pwm_timer_channel;
	GPIO_TypeDef* dir_port;
	uint16_t dir_pin;
	int8_t build_direction;
} motor_config_t;


class Motor {
public:
	Motor();
	void init(motor_config_t config);

	void start();
	void stop();

	void setSpeed(float speed);
	float getSpeed();

	friend class FRODO_Drive;

private:

	void setPWM(float dutycycle);
	void setDirection(int8_t direction);

	float speed;
	int8_t direction;
	bool state;

	motor_config_t config;

};



#endif /* MOTORS_H_ */
