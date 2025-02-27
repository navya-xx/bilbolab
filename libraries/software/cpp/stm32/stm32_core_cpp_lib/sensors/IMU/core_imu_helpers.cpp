/*
 * core_imu_helpers.cpp
 *
 *  Created on: Jul 8, 2022
 *      Author: Dustin Lehmann
 */

#include "core_imu_helpers.h"

#if CORE_CONFIG_USE_SPI

float gyr_x[128];
float gyr_y[128];
float gyr_z[128];

// TODO: This is blocking and annoying
bmi160_gyr_calib_t core_sensors_GyroCalibration(BMI160 *imu, uint8_t samples,
		bool resetCalibration) {

	bmi160_gyr_calib_t calib;

	if (resetCalibration) {
		imu->gyr_calib.x = 0.0;
		imu->gyr_calib.y = 0.0;
		imu->gyr_calib.z = 0.0;
	}

	for (int i = 0; i < samples; i++) {
		imu->update();
		gyr_x[i] = imu->gyr.x;
		gyr_y[i] = imu->gyr.y;
		gyr_z[i] = imu->gyr.z;

		osDelay(50);
	}

	calib.x = mean(gyr_x, samples);
	calib.y = mean(gyr_y, samples);
	calib.z = mean(gyr_z, samples);

	return calib;

}
#endif
