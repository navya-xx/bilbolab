/*
 * motors.cpp
 *
 *  Created on: May 7, 2024
 *      Author: Dustin Lehmann
 */

#include "frodo_motors.h"
#include "frodo_drive.h"

Motor::Motor() {

}

void Motor::init(motor_config_t config){
	this->config = config;

	this->state = false;
	this->setDirection(1);
}

/* ------------------------------------------------------------------------ */
void Motor::setSpeed(float speed){

	if (this->state == 0){
			return;
		}

	if (speed >= 0) {
		this->setDirection(1);
	} else {
		this->setDirection(-1);
	}
	this->speed = speed;

	this->setPWM(fabs(speed));
}

/* ------------------------------------------------------------------------ */
void Motor::setPWM(float dutycycle){
	uint32_t arr = (uint32_t) __HAL_TIM_GET_AUTORELOAD(this->config.pwm_timer);
	uint32_t ocv = (uint32_t) (dutycycle * (float) arr);

	if (this->config.pwm_timer->Instance == TIM5 || this->config.pwm_timer->Instance == TIM2) {
		__HAL_TIM_SetCompare(this->config.pwm_timer,this->config.pwm_timer_channel, (uint32_t) ocv);
	} else {
		__HAL_TIM_SetCompare(this->config.pwm_timer,this->config.pwm_timer_channel, (uint16_t) ocv);
	}
}

/* ------------------------------------------------------------------------ */
void Motor::setDirection(int8_t direction){

	this->direction = direction;

	int8_t dir = direction * this->config.build_direction;

	if (dir == 1) {
		HAL_GPIO_WritePin(this->config.dir_port, this->config.dir_pin, GPIO_PIN_SET);
	} else {
		HAL_GPIO_WritePin(this->config.dir_port, this->config.dir_pin, GPIO_PIN_RESET);
	}
}

/* ------------------------------------------------------------------------ */
void Motor::start(){

	this->state = 1;
	HAL_TIM_PWM_Start(this->config.pwm_timer, this->config.pwm_timer_channel);
	__HAL_TIM_SetCompare(this->config.pwm_timer, this->config.pwm_timer_channel, 0);

}

/* ------------------------------------------------------------------------ */
void Motor::stop(){
	this->state = 0;
	HAL_TIM_PWM_Stop(this->config.pwm_timer, this->config.pwm_timer_channel);
}

