/*
 * amt22.h
 *
 *  Created on: Jul 22, 2024
 *      Author: Dustin Lehmann
 */

#ifndef SENSORS_AMT22_AMT22_H_
#define SENSORS_AMT22_AMT22_H_

#include "stm32h7xx.h"


typedef struct AMT22_config_t {
	SPI_HandleTypeDef* hspi;
	GPIO_TypeDef* cs_port;
	uint16_t cs_pin;
} AMT22_config_t;

class AMT22 {
public:
	AMT22();

	void init(AMT22_config_t config);
	void start();


	void reset();
	void update();
	void setZeroPoint();
	float getPosition();


	uint16_t position_raw;


private:
	void readPosition();
	uint8_t rx_buf[2];
	AMT22_config_t _config;
};





#endif /* SENSORS_AMT22_AMT22_H_ */
