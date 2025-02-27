/*
 * encoder.h
 *
 *  Created on: May 26, 2024
 *      Author: Dustin Lehmann
 */

#ifndef HARDWARE_ENCODER_ENCODER_H_
#define HARDWARE_ENCODER_ENCODER_H_

#include "stm32h7xx_hal.h"

typedef struct encoder_config_t {
	TIM_TypeDef* htim;
	uint16_t counts_per_rev;
} encoder_config_t;

class Encoder {
public:
	Encoder();
	void init(encoder_config_t config);


private:

};




#endif /* HARDWARE_ENCODER_ENCODER_H_ */
