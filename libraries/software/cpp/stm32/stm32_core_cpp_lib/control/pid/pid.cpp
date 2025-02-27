/*
 * pid.cpp
 *
 *  Created on: Oct 29, 2024
 *      Author: Dustin Lehmann
 */

#include "pid.h"
#include "math.h"

float sgn(float input) {
	if (input >= 0) {
		return 1;
	} else {
		return -1;
	}
}

PID_Control::PID_Control() {

}

void PID_Control::init(pid_control_config_t config) {
	this->config = config;
	this->reset();
}

void PID_Control::reset() {
	this->error_integral = 0;
	this->error_last = 0;
	this->last_output = 0;
}

float PID_Control::update(float error) {
	float output = this->config.Kp * error
			+ this->config.Ki * this->error_integral
			+ this->config.Kd * 1.0 / this->config.Ts
					* (error - this->error_last);

	this->error_last = error;

	this->error_integral = this->error_integral + this->config.Ts * error;

	if (this->config.enable_integral_limit && abs(this->error_integral) > this->config.error_integral_limit) {
		this->error_integral = sgn(this->error_integral)
				* this->config.error_integral_limit;
	}

	if (this->config.enable_output_limit) {
		if (output > this->config.output_limit_max) {
			output = this->config.output_limit_max;
		}
		if (output < this->config.output_limit_min) {
			output = this->config.output_limit_min;
		}
	}

	if (this->config.enable_rate_limit){
		float d_u = (output-this->last_output)/this->config.Ts;

		if(d_u > this->config.rate_limit_max){
			output = this->last_output + this->config.rate_limit_max * this->config.Ts;
		}
		else if (d_u < this->config.rate_limit_min){
			output = this->last_output + this->config.rate_limit_min * this->config.Ts;
		}
	}

	this->last_output = output;

	return output;
}
