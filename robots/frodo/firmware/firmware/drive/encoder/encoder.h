/*
 * encoder.h
 *
 *  Created on: May 7, 2024
 *      Author: Dustin Lehmann
 */

#ifndef ENCODER_H_
#define ENCODER_H_

#include "core.h"
#include "stm32h7xx_hal.h"
#include "firmware_settings.h"
#include <math.h>

#define IMPULSE_PER_ROTATION 6 /* Impulse per Rotation */
#define REDUCTION_RATIO 33 /* Reduction Ratio */
#define WHEEL_RADIUS_MM 19 /* Wheel Radius in mm */
#define WINDOW_SIZE 4


typedef struct encoder_config_t {
	TIM_HandleTypeDef* tim;
	int update_time_ms;
	float velocity_scale;
} encoder_config_t;

class Encoder{
public:

	Encoder();

	void init(encoder_config_t config);
	void start();
	void update();

	void read();
	float getRPM();
	float getVelocity();

private:
	void _updateIndex();

	encoder_config_t config;
	int reading_index;
	int readings[WINDOW_SIZE];

};


#define MAX_ENCODERS 2

typedef struct input_capture_encoder_config_t {
	TIM_HandleTypeDef* htim;
	uint32_t channel;
	uint32_t timer_frequency;
	uint32_t timer_prescaler;
	uint32_t ticks_per_revolution;
} input_capture_encoder_config_t;

class InputCaptureEncoder {
public:
	InputCaptureEncoder();
	void init(input_capture_encoder_config_t config);
	void start();


	float getRPM();
	float getVelocity();


	void ic_interrupt_handler(uint16_t value);
	void timer_overflow_handler();


	uint32_t value_buffer[MOTOR_INPUT_CAPTURE_BUFFER_SIZE] = {0};
	int buffer_index = 0;

	input_capture_encoder_config_t config;

private:

	void _appendValue(uint32_t value);
	uint32_t _getMeanValue();

	float _tick_time;
	uint16_t previous_ic_tick = 0;


};

void tim_period_elapsed_callback(TIM_HandleTypeDef* htim);
void tim_ic_callback(TIM_HandleTypeDef* htim);



#endif /* ENCODER_H_ */
