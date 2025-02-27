/*
 * math.h
 *
 *  Created on: 7 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_UTILS_CORE_MATH_H_
#define CORE_UTILS_CORE_MATH_H_

#include "stdint.h"

const float pi = 3.14159265;

inline float deg2rad(float angle) {
	return angle * pi / 180.0;
}

inline float rad2deg(float angle) {
	return angle * 180.0 / pi;
}

float mean(float* data, uint16_t len);

float limit(float data, float min_value, float max_value);
float limit(float data, float max_value);


#endif /* CORE_UTILS_CORE_MATH_H_ */
