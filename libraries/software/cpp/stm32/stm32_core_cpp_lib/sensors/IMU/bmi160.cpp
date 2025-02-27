/*
 * bmi160.c
 *
 *  Created on: Jul 7, 2022
 *      Author: lehmann_workstation
 */

#include "bmi160.h"

#if CORE_CONFIG_USE_SPI

BMI160::BMI160(){

}

/* ============================================================================= */
uint8_t BMI160::writeRegister(uint8_t reg, uint8_t data) {
	HAL_GPIO_WritePin(this->_config.CS_GPIOx, this->_config.CS_GPIO_Pin, GPIO_PIN_RESET);
	HAL_SPI_Transmit(this->_config.hspi, &reg, 1, 1);
	HAL_SPI_Transmit(this->_config.hspi, &data, 1, 1);
	HAL_GPIO_WritePin(this->_config.CS_GPIOx, this->_config.CS_GPIO_Pin, GPIO_PIN_SET);

	return CORE_OK;
}

/* ============================================================================= */
uint8_t BMI160::init(bmi160_config_t config) {

	this->_config = config;
	// Make a dummy read to turn on SPI mode
//	this->readRegister(0x7F);
	HAL_GPIO_WritePin(this->_config.CS_GPIOx, this->_config.CS_GPIO_Pin, GPIO_PIN_SET);
	delay(250);

	// Check if the IMU can be addressed
	if (not (this->check())) {
		return 0;
		core_ErrorHandler(CORE_ERROR_HARDWARE_IMU);
	}

	// Reset the IMU to delete all previously loaded registers
	this->reset();

	// Wait until the reset is finished
	delay(250);

	// Make a dummy read again to turn on SPI
	this->readRegister(0x7F);

	// Set the power mode to normal in order for all registers to be writable
	this->setPowerMode(BMI160_Power_Normal);

	// Set the accelerometer setting
	this->setAccConfig(this->_config.acc.odr | this->_config.acc.bw,
			this->_config.acc.range);

	// Set the gyroscope setting
	this->setGyroConfig(this->_config.gyr.odr | this->_config.gyr.bw,
			this->_config.gyr.range);

	// Check if the settings have been set correctly

	uint8_t acc_config_reg = this->readRegister(BMI160_REG_ACCEL_CONFIG);
	uint8_t acc_range_reg = this->readRegister(BMI160_REG_ACCEL_RANGE);
	uint8_t gyr_config_reg = this->readRegister(BMI160_REG_GYRO_CONFIG);
	uint8_t gyr_range_reg = this->readRegister(BMI160_REG_GYRO_RANGE);

	if (acc_config_reg != (this->_config.acc.odr | this->_config.acc.bw)) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_IMU);
	}
	if (acc_range_reg != this->_config.acc.range) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_IMU);
	}
	if (gyr_config_reg != (this->_config.gyr.odr | this->_config.gyr.bw)) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_IMU);
	}
	if (gyr_range_reg != this->_config.gyr.range) {
		core_ErrorHandler(CORE_ERROR_HARDWARE_IMU);
	}

	return CORE_OK;
}

/* ============================================================================= */
uint8_t BMI160::readRegister(uint8_t reg) {
	uint8_t ret = 0;
	reg |= 0x80;

	HAL_GPIO_WritePin(this->_config.CS_GPIOx, this->_config.CS_GPIO_Pin, GPIO_PIN_RESET);
	HAL_SPI_Transmit(this->_config.hspi, &reg, 1, 10);
	HAL_SPI_Receive(this->_config.hspi, &ret, 1, 10);
	HAL_GPIO_WritePin(this->_config.CS_GPIOx, this->_config.CS_GPIO_Pin, GPIO_PIN_SET);

	return ret;
}

/* ============================================================================= */
uint8_t BMI160::readMultipleRegister(uint8_t reg, uint8_t *data, uint8_t len) {
//	reg += 0x80;
	reg |= 0x80;

	HAL_GPIO_WritePin(this->_config.CS_GPIOx, this->_config.CS_GPIO_Pin, GPIO_PIN_RESET);
	HAL_SPI_Transmit(this->_config.hspi, &reg, 1, 10);
	HAL_SPI_Receive(this->_config.hspi, data, len, 10);
	HAL_GPIO_WritePin(this->_config.CS_GPIOx, this->_config.CS_GPIO_Pin, GPIO_PIN_SET);

	return CORE_OK;
}

/* ============================================================================= */
uint8_t BMI160::check() {
	uint8_t id = this->readID();
	if (id != 209) {
		return 0;
	}

	return CORE_OK;
}

/* ============================================================================= */
uint8_t BMI160::readID() {
	return this->readRegister(BMI160_REG_CHIP_ID);
}

/* ============================================================================= */
void BMI160::update() {
	this->fetchData();
	this->processData();
}

/* ============================================================================= */
uint8_t BMI160::fetchData() {
//	this->readSensorTime();
	this->readGyr();
	this->readAcc();

	return 1;
}

/* ============================================================================= */
uint8_t BMI160::processData() {

	// Gyroscope
	switch (this->_config.gyr.range) {
	case BMI160_GYRO_RANGE_125_DPS: {
		this->gyr.x = deg2rad(this->gyr_raw.x / 32768.0 * 125.0)
				- this->gyr_calib.x;
		this->gyr.y = deg2rad(this->gyr_raw.y / 32768.0 * 125.0)
				- this->gyr_calib.y;
		this->gyr.z = deg2rad(this->gyr_raw.z / 32768.0 * 125.0)
				- this->gyr_calib.z;
		break;
	}
	case BMI160_GYRO_RANGE_250_DPS: {
		this->gyr.x = deg2rad(this->gyr_raw.x / 32768.0 * 250.0)
				- this->gyr_calib.x;
		this->gyr.y = deg2rad(this->gyr_raw.y / 32768.0 * 250.0)
				- this->gyr_calib.y;
		this->gyr.z = deg2rad(this->gyr_raw.z / 32768.0 * 250.0)
				- this->gyr_calib.z;
		break;
	}
	case BMI160_GYRO_RANGE_500_DPS: {
		this->gyr.x = deg2rad(this->gyr_raw.x / 32768.0 * 500.0)
				- this->gyr_calib.x;
		this->gyr.y = deg2rad(this->gyr_raw.y / 32768.0 * 500.0)
				- this->gyr_calib.y;
		this->gyr.z = deg2rad(this->gyr_raw.z / 32768.0 * 500.0)
				- this->gyr_calib.z;
		break;
	}
	case BMI160_GYRO_RANGE_1000_DPS: {
		this->gyr.x = deg2rad(this->gyr_raw.x / 32768.0 * 1000.0)
				- this->gyr_calib.x;
		this->gyr.y = deg2rad(this->gyr_raw.y / 32768.0 * 1000.0)
				- this->gyr_calib.y;
		this->gyr.z = deg2rad(this->gyr_raw.z / 32768.0 * 1000.0)
				- this->gyr_calib.z;
		break;
	}
	case BMI160_GYRO_RANGE_2000_DPS: {
		this->gyr.x = deg2rad(this->gyr_raw.x / 32768.0 * 2000.0)
				- this->gyr_calib.x;
		this->gyr.y = deg2rad(this->gyr_raw.y / 32768.0 * 2000.0)
				- this->gyr_calib.y;
		this->gyr.z = deg2rad(this->gyr_raw.z / 32768.0 * 2000.0)
				- this->gyr_calib.z;
		break;
	}
	}

	// Accelerometer
	switch (this->_config.acc.range) {
	case BMI160_ACCEL_RANGE_2G: {
		this->acc.x = this->acc_raw.x / 32768.0 * 2.0 * 9.81;
		this->acc.y = this->acc_raw.y / 32768.0 * 2.0 * 9.81;
		this->acc.z = this->acc_raw.z / 32768.0 * 2.0 * 9.81;
		break;
	}
	case BMI160_ACCEL_RANGE_4G: {
		this->acc.x = this->acc_raw.x / 32768.0 * 4.0 * 9.81;
		this->acc.y = this->acc_raw.y / 32768.0 * 4.0 * 9.81;
		this->acc.z = this->acc_raw.z / 32768.0 * 4.0 * 9.81;
		break;
	}
	case BMI160_ACCEL_RANGE_8G: {
		this->acc.x = this->acc_raw.x / 32768.0 * 8.0 * 9.81;
		this->acc.y = this->acc_raw.y / 32768.0 * 8.0 * 9.81;
		this->acc.z = this->acc_raw.z / 32768.0 * 8.0 * 9.81;
		break;
	}
	case BMI160_ACCEL_RANGE_16G: {
		this->acc.x = this->acc_raw.x / 32768.0 * 16.0 * 9.81;
		this->acc.y = this->acc_raw.y / 32768.0 * 16.0 * 9.81;
		this->acc.z = this->acc_raw.z / 32768.0 * 16.0 * 9.81;
		break;
	}
	}

	return 1;
}

/* ============================================================================= */
void BMI160::setCalibration(float gyr_x, float gyr_y, float gyr_z) {
	this->gyr_calib.x = gyr_x;
	this->gyr_calib.y = gyr_y;
	this->gyr_calib.z = gyr_z;
}

/* ============================================================================= */
uint8_t BMI160::readGyr() {
	uint8_t gyr_data[6] = { 0 };
	this->readMultipleRegister(BMI160_REG_GYR_X_LOW, gyr_data, 6);

	this->gyr_raw.x = bytearray_to_int16(&gyr_data[0]);
	this->gyr_raw.y = bytearray_to_int16(&gyr_data[2]);
	this->gyr_raw.z = bytearray_to_int16(&gyr_data[4]);

	return 1;
}

/* ============================================================================= */
uint8_t BMI160::readAcc() {
	uint8_t acc_data[6] = { 0 };
	this->readMultipleRegister(BMI160_REG_ACC_X_LOW, acc_data, 6);

	this->acc_raw.x = bytearray_to_int16(&acc_data[0]);
	this->acc_raw.y = bytearray_to_int16(&acc_data[2]);
	this->acc_raw.z = bytearray_to_int16(&acc_data[4]);

	return 1;
}

/* ============================================================================= */
uint8_t BMI160::readSensorTime() {
	uint8_t sensortime_data[4] = { 0 };
	this->readMultipleRegister(BMI160_REG_SENSORTIME_0, sensortime_data, 3);
	this->sensortime = bytearray_to_uint32(sensortime_data);
	return CORE_OK;
}

/* ============================================================================= */
uint8_t BMI160::setGyroConfig(uint8_t config, uint8_t range) {

	this->writeRegister(BMI160_REG_GYRO_RANGE, range);
	this->writeRegister(BMI160_REG_GYRO_CONFIG, config);

	return CORE_OK;
}

/* ============================================================================= */
uint8_t BMI160::setAccConfig(uint8_t config, uint8_t range) {
	this->writeRegister(BMI160_REG_ACCEL_CONFIG, config);
	this->writeRegister(BMI160_REG_ACCEL_RANGE, range);

	return CORE_OK;
}

/* ============================================================================= */
uint8_t BMI160::setPowerMode(BMI160_PowerMode mode) {
	if (mode == BMI160_Power_Normal) {
		delay(100);
		this->writeRegister(BMI160_REG_COMMAND, BMI160_GYRO_NORMAL_MODE);
		delay(250);
		this->writeRegister(BMI160_REG_COMMAND, BMI160_ACCEL_NORMAL_MODE);
		delay(250);
	} else if (mode == BMI160_Power_Suspend) {
		this->writeRegister(BMI160_REG_COMMAND, BMI160_ACCEL_SUSPEND_MODE);
		delay(100);
		this->writeRegister(BMI160_REG_COMMAND, BMI160_GYRO_SUSPEND_MODE);
		delay(100);
	}
	return CORE_OK;
}

/* ============================================================================= */
void BMI160::fastOffsetCalibration() {
	// Configure the FOC register
	uint8_t foc_data = 0;

	if (this->_config.gyr.foc_enable) {
		foc_data = BMI160_FOC_GYRO_ENABLE;
	} else {
		foc_data = BMI160_FOC_GYRO_DISABLE;
	}

	if (this->_config.acc.foc_enable) {
		core_ErrorHandler(5);
	}

	this->writeRegister(BMI160_REG_FOC, foc_data);
	delay(10);

	// Perform the FOC
	this->writeRegister(BMI160_REG_COMMAND, BMI160_CMD_FAST_OFFSET_CALIBRATION);

	// Wait until the FOC is finished

	uint8_t foc_finished = 0;
	uint8_t status = 0;
	while (foc_finished == 0) {
		status = this->readRegister(0x1B);
		foc_finished = status & 0b00001000;
		delay(10);
	}

	uint8_t offset_register = this->readRegister(0x77);

	// enable the offset compensation for the gyroscope
	offset_register |= 0b10000000;
	this->writeRegister(0x77, offset_register);

}

/* ============================================================================= */
void BMI160::reset() {
	this->writeRegister(BMI160_REG_COMMAND, 0xB6);
	delay(10);
}
#endif
