/*
 * pid.h
 *
 *  Created on: Oct 29, 2024
 *      Author: Dustin Lehmann
 */

#ifndef CONTROL_PID_PID_H_
#define CONTROL_PID_PID_H_

typedef struct pid_control_config_t {
	float Kp;
	float Ki;
	float Kd;

	float Ts;

	bool enable_integral_limit = false;
	float error_integral_limit = 0;

	bool enable_output_limit = false;
	float output_limit_max = 0;
	float output_limit_min = 0;

	bool enable_rate_limit = false;
	float rate_limit_max = 0;
	float rate_limit_min = 0;

} pid_control_config_t;

class PID_Control {
public:
	PID_Control();

	void init(pid_control_config_t config);
	float update(float error);
	void reset();

	pid_control_config_t config;

	float error_integral;
	float last_output;
	float error_last;

private:



};

#endif /* CONTROL_PID_PID_H_ */
