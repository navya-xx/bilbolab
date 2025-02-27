/*
 * speed-control.cpp
 *
 *  Created on: May 17, 2024
 *      Author: Jarne Bärmann
 */

#include <drive/frodo_drive.h>

FRODO_Drive::FRODO_Drive() {

}

void FRODO_Drive::init(frodo_drive_config_t config) {
	this->config = config;
	{
		motor_config_t motor_left_config = { .pwm_timer =
				this->config.motor_left_htim, .pwm_timer_channel =
				this->config.motor_left_timer_channel, .dir_port =
				this->config.motor_left_dir_port, .dir_pin =
				this->config.motor_left_dir_pin, .build_direction =
				this->config.motor_left_direction };
		this->motor_left.init(motor_left_config);
	}

	{
		motor_config_t motor_right_config = { .pwm_timer =
				this->config.motor_right_htim, .pwm_timer_channel =
				this->config.motor_right_timer_channel, .dir_port =
				this->config.motor_right_dir_port, .dir_pin =
				this->config.motor_right_dir_pin, .build_direction =
				this->config.motor_right_direction };
		this->motor_right.init(motor_right_config);
	}

	{
		encoder_config_t encoder_left_config = { .tim =
				this->config.motor_left_encoder_htim, .update_time_ms =
				this->config.update_time_ms, .velocity_scale =
				this->config.motor_left_velocity_scale };
		this->encoder_left.init(encoder_left_config);
	}

	{
		encoder_config_t encoder_right_config = { .tim =
				this->config.motor_right_encoder_htim, .update_time_ms =
				this->config.update_time_ms, .velocity_scale =
				this->config.motor_right_velocity_scale };
		this->encoder_right.init(encoder_right_config);
	}
}

void FRODO_Drive::start() {
	this->motor_left.start();
	this->motor_right.start();

	this->encoder_left.start();
	this->encoder_right.start();
}

void FRODO_Drive::update() {
	this->encoder_left.update();
	this->encoder_right.update();
}

frodo_drive_sample_t FRODO_Drive::getSample(){
	frodo_drive_sample_t sample = {
			.speed = this->getSpeed(),
			.goal_speed = this->getGoalSpeed(),
			.rpm = this->getRPM()
	};
	return sample;
}

motor_speed_t FRODO_Drive::getGoalSpeed(){
	motor_speed_t ret = {
			.left = this->motor_left.speed,
			.right = this->motor_right.speed
	};
	return ret;
}

motor_speed_t FRODO_Drive::getSpeed() {
	motor_speed_t ret = {
			.left = this->motor_left.direction * this->encoder_left.getVelocity(),
			.right = this->motor_right.direction * this->encoder_right.getVelocity()
	};
	return ret;
}

motor_rpm_t FRODO_Drive::getRPM() {
	motor_rpm_t ret = {
			.left = this->motor_left.direction * this->encoder_left.getRPM(),
			.right = this->motor_right.direction * this->encoder_right.getRPM() };
	return ret;
}

void FRODO_Drive::setSpeed(motor_input_t input) {
	this->motor_left.setSpeed(input.left);
	this->motor_right.setSpeed(input.right);
}

