/*
 * amt22.cpp
 *
 *  Created on: Jul 22, 2024
 *      Author: Dustin Lehmann
 */

#include "amt22.h"

const float PI = 3.14159265358979323846;

double wrapToPi(double angle) {
    // Wrap the angle within -π to π
    while (angle <= -PI) angle += 2.0 * PI;
    while (angle > PI) angle -= 2.0 * PI;
    return angle;
}

AMT22::AMT22() {

}

void AMT22::init(AMT22_config_t config) {
	this->_config = config;
	this->position_raw = 0;
	this->rx_buf[0] = 0;
	this->rx_buf[1] = 0;
}

void AMT22::start() {

}

void AMT22::reset() {
	uint8_t tx_buf[] = {0x00, 0x60};
	HAL_GPIO_WritePin(this->_config.cs_port, this->_config.cs_pin, GPIO_PIN_RESET);
	HAL_SPI_Transmit(this->_config.hspi, tx_buf, 2, 10);
	HAL_GPIO_WritePin(this->_config.cs_port, this->_config.cs_pin, GPIO_PIN_SET);
}

void AMT22::update() {
	this->readPosition();
}

void AMT22::readPosition() {
	HAL_GPIO_WritePin(this->_config.cs_port, this->_config.cs_pin, GPIO_PIN_RESET);
	HAL_SPI_Receive(this->_config.hspi, rx_buf, 2, 10);
	HAL_GPIO_WritePin(this->_config.cs_port, this->_config.cs_pin, GPIO_PIN_SET);

	uint8_t first_byte = rx_buf[0] & 0b00111111;
	uint8_t second_byte = rx_buf[1];

	this->position_raw = first_byte << 8 | second_byte;
}

void AMT22::setZeroPoint() {
	uint8_t tx_buf[] = {0x00, 0x70};
	HAL_GPIO_WritePin(this->_config.cs_port, this->_config.cs_pin, GPIO_PIN_RESET);
	HAL_SPI_Transmit(this->_config.hspi, tx_buf, 2, 10);
	HAL_GPIO_WritePin(this->_config.cs_port, this->_config.cs_pin, GPIO_PIN_SET);
}

float AMT22::getPosition() {
	return wrapToPi(this->position_raw / 16383 * 2 * PI);
}


