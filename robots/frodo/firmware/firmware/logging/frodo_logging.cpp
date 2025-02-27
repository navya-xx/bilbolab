/*
 * twipr_logging.cpp
 *
 *  Created on: Nov 20, 2024
 *      Author: lehmann
 */

#include "frodo_logging.h"
#include "firmware.hpp"

FRODO_Logging::FRODO_Logging() {

}

void FRODO_Logging::init(frodo_logging_config_t config) {
	this->config = config;
}

void FRODO_Logging::start() {

}

frodo_logging_buffer_status_t FRODO_Logging::collectSamples() {

	this->current_sample.general = this->config.firmware->getSample();
	this->current_sample.drive = this->config.drive->getSample();

	if (this->config.use_buffer) {
		this->sample_buffer[this->sample_index].general =
				this->config.firmware->getSample();
		this->sample_buffer[this->sample_index].drive =
				this->config.drive->getSample();

		this->sample_index++;

		if (this->sample_index == FRODO_FIRMWARE_SAMPLE_BUFFER_SIZE) {
			this->sample_index = 0;
			return FRODO_LOGGING_BUFFER_FULL;
		}
	}
	return FRODO_LOGGING_BUFFER_NOT_FULL;
}

frodo_sample_t FRODO_Logging::getCurrentSample() {
	return this->current_sample;
}
