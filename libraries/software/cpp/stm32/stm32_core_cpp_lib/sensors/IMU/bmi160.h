/*
 * bmi160.h
 *
 *  Created on: Jul 7, 2022
 *      Author: lehmann_workstation
 */

#ifndef CORE_SENSORS_IMU_BMI160_H_
#define CORE_SENSORS_IMU_BMI160_H_

#include "../../core_includes.h"
#include "../../utils/core_utils.h"

#include "bmi160_defs.h"

#define BMI160_REG_CHIP_ID	0x00


typedef struct bmi160_gyr_raw {
	int16_t x;
	int16_t y;
	int16_t z;
} bmi160_gyr_raw;

typedef struct bmi160_gyr {
	float x;
	float y;
	float z;
} bmi160_gyr;

typedef struct bmi160_acc_raw {
	int16_t x;
	int16_t y;
	int16_t z;
} bmi160_acc_raw;

typedef struct bmi160_acc {
	float x;
	float y;
	float z;
} bmi160_acc;

typedef struct bmi160_gyr_calib_t {
	float x = 0.0;
	float y = 0.0;
	float z = 0.0;
} bmi160_gyr_calib_t;

typedef struct bmi160_acc_config_t {
	uint8_t odr = BMI160_ACCEL_ODR_400HZ;
	uint8_t bw = BMI160_ACCEL_BW_NORMAL_AVG4;
	uint8_t range = BMI160_ACCEL_RANGE_8G;
	uint8_t foc_enable = 0;
} bmi160_acc_config_t;

typedef struct bmi160_gyr_config_t {
	uint8_t odr = BMI160_GYRO_ODR_800HZ;
	uint8_t bw = BMI160_GYRO_BW_NORMAL_MODE;
	uint8_t range = BMI160_GYRO_RANGE_2000_DPS;
	uint8_t foc_enable = 1;
} bmi160_gyr_config_t;

typedef struct bmi160_config_t {
	SPI_HandleTypeDef *hspi;
	GPIO_TypeDef *CS_GPIOx;
	uint16_t CS_GPIO_Pin;
	bmi160_gyr_config_t gyr;
	bmi160_acc_config_t acc;
} bmi160_config_t;

enum BMI160_PowerMode {
	BMI160_Power_Normal, BMI160_Power_Suspend
};

class BMI160 {
public:
	BMI160();

	uint8_t init(bmi160_config_t config);

	void reset();

	uint8_t check();
	uint8_t readID();

	void update();
	uint8_t fetchData();
	uint8_t processData();

	void setCalibration(float gyr_x, float gyr_y, float gyr_z);
	void fastOffsetCalibration();

	uint8_t readAcc();
	uint8_t readGyr();
	uint8_t readSensorTime();

	uint8_t setGyroConfig(uint8_t config, uint8_t range);
	uint8_t setAccConfig(uint8_t config, uint8_t range);
	uint8_t setPowerMode(BMI160_PowerMode mode);

	uint8_t writeRegister(uint8_t reg, uint8_t data);
	uint8_t readRegister(uint8_t reg);
	uint8_t readMultipleRegister(uint8_t reg, uint8_t *data, uint8_t len);

	bmi160_gyr_raw gyr_raw;
	bmi160_gyr gyr;
	bmi160_acc_raw acc_raw;
	bmi160_acc acc;
	uint32_t sensortime;
	bmi160_gyr_calib_t gyr_calib;
private:

	bmi160_config_t _config;

};
#endif /* CORE_SENSORS_IMU_BMI160_H_ */
