/*
 * twipr_model.h
 *
 *  Created on: 22 Feb 2023
 *      Author: Dustin Lehmann
 */

#ifndef ESTIMATION_TWIPR_MODEL_H_
#define ESTIMATION_TWIPR_MODEL_H_

typedef struct twipr_model_t {
	float m;
	float r_wheel;
	float distance_wheels;
	float l_cg;
	float l_imu;
} twipr_model;

extern twipr_model_t twipr_model_small;


#endif /* ESTIMATION_TWIPR_MODEL_H_ */
