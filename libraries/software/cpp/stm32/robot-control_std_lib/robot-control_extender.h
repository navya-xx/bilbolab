/*
 * robot-control_extender.h
 *
 *  Created on: Apr 24, 2024
 *      Author: Dustin Lehmann
 */

#ifndef ROBOT_CONTROL_EXTENDER_H_
#define ROBOT_CONTROL_EXTENDER_H_

#include <core.h>
#include <robot-control_extender_registers.h>


#define EXTENDER_ADDRESS 0x02

typedef struct extender_config_struct_t {
	I2C_HandleTypeDef* hi2c;
} extender_config_struct_t ;


typedef struct rgb_color_struct_t {
	uint8_t red;
	uint8_t green;
	uint8_t blue;
}rgb_color_struct_t;

class RobotControl_Extender {
public:
	RobotControl_Extender();

	void init(extender_config_struct_t config);
	void start();

	void setStatusLED(int8_t status);

	void rgbLED_intern_setMode(uint8_t position,uint8_t mode);
	void rgbLED_intern_setColor(uint8_t position,uint8_t red, uint8_t green, uint8_t blue);
	void rgbLED_intern_setState(uint8_t position,uint8_t state);
	void rgbLED_intern_blink(uint8_t position, uint16_t on_time_ms);

//	void rgbLEDStrip_extern_setColor(uint8_t red, uint8_t green, uint8_t blue);
	void rgbLEDStrip_extern_setColor(rgb_color_struct_t color);

	void buzzer_setConfig(float frequency, uint16_t on_time, uint8_t repeats);
	void buzzer_start();

private:

	extender_config_struct_t config;
};



#endif /* ROBOT_CONTROL_EXTENDER_H_ */
