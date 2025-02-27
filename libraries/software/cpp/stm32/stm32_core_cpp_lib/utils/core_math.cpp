/*
 * math.cpp
 *
 *  Created on: 7 Jul 2022
 *      Author: Dustin Lehmann
 */

#include "core_math.h"

float mean(float *data, uint16_t len) {
	float sum = 0;

	for (uint16_t i = 0; i < len; i++) {
		sum += data[i];
	}

	return sum / len;
}


float limit(float data, float min_value, float max_value){
	if (data > max_value){
		data = max_value;
	}
	if (data < min_value){
		data = min_value;
	}
	return data;
}


float limit(float data, float max_value){
	return limit(data, -max_value, max_value);
}
