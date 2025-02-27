/*
 * robot-control_default_config.h
 *
 *  Created on: 29 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef ROBOT_CONTROL_DEFAULT_CONFIG_H_
#define ROBOT_CONTROL_DEFAULT_CONFIG_H_



#if ROBOT-CONTROL_CONFIG_OVERRIDE
#include <robot-control_config.h>
#else

// Sensors

#define RC_SENSOR_LOOP_FREQ 100.0f // This is the frequency the sensor fusion will be run


#endif



#endif /* ROBOT_CONTROL_DEFAULT_CONFIG_H_ */
