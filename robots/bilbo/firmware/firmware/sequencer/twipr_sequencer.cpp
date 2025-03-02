/*
 * twipr_sequencer.cpp
 *
 *  Created on: Nov 20, 2024
 *      Author: Dustin Lehmann
 */

#include "twipr_sequencer.h"
#include "twipr_communication.h"
#include "robot-control_std.h"

_RAM_D2 twipr_sequence_input_t rx_sequence_buffer[TWIPR_SEQUENCE_BUFFER_SIZE ];
_RAM_D2 twipr_sequence_input_t sequence_buffer[TWIPR_SEQUENCE_BUFFER_SIZE ];

TWIPR_Sequencer::TWIPR_Sequencer() {

}

/* =============================================================== */
void TWIPR_Sequencer::init(twipr_sequencer_config_t config) {
	this->config = config;
	this->sequence_tick = 0;
	this->mode = TWIPR_SEQUENCER_MODE_IDLE;

	this->config.comm->callbacks.new_trajectory.registerFunction(this,
			&TWIPR_Sequencer::spiSequenceReceived_callback);

	this->config.control->callbacks.mode_change.registerFunction(this,
			&TWIPR_Sequencer::modeChange_callback);
}
/* =============================================================== */
void TWIPR_Sequencer::start() {

}

/* =============================================================== */
void TWIPR_Sequencer::update() {

	if (this->mode == TWIPR_SEQUENCER_MODE_IDLE) {
		return;
	}

	// Do the Update

}
/* =============================================================== */
void TWIPR_Sequencer::startSequence(uint16_t id) {
	this->sequence_tick = 0;

	// Check the requirements
	if (!this->_sequence_received) {
		return;
	}

	// Check the control mode
	if (this->config.control->mode != this->loaded_sequence.control_mode) {
		return;
	}

	// Check if the loaded sequence has the same id
	if (this->loaded_sequence.sequence_id != id) {
		return;
	}

	this->mode = TWIPR_SEQUENCER_MODE_RUNNING;

	// Disable External Inputs to the controller
	this->config.control->disableExternalInput();

	// Give an audio queue
	rc_buzzer.setConfig(900, 100, this->loaded_sequence.sequence_id);
	rc_buzzer.start();

	// Call the callback(s)
	if (this->_callbacks.started.registered) {
		this->_callbacks.started.call((uint16_t) id);
	}
}

/* =============================================================== */
void TWIPR_Sequencer::abortSequence() {

	// TODO: I need to reflect in the sample if the sequence was finished or aborted

	// Enable external inputs to the controller
	this->config.control->enableExternalInput();

	// Set the mode
	this->mode = TWIPR_SEQUENCER_MODE_ERROR;

	// Give an audio queue
	rc_buzzer.setConfig(900, 100, 3);
	rc_buzzer.start();

	// TODO: Send Data to Host

	//
	if (this->_callbacks.aborted.registered) {
		this->_callbacks.aborted.call(
				(uint16_t) this->loaded_sequence.sequence_id);
	}
}

/* =============================================================== */
void TWIPR_Sequencer::finishSequence() {

	// Enable external inputs to the controller
	this->config.control->enableExternalInput();

	// Set the mode
	this->mode = TWIPR_SEQUENCER_MODE_IDLE;

	// Give an audio queue
	rc_buzzer.setConfig(900, 150, this->loaded_sequence.sequence_id);
	rc_buzzer.start();

	// TODO: Send Data to host

	//
	if (this->_callbacks.finished.registered) {
		this->_callbacks.finished.call(
				(uint16_t) this->loaded_sequence.sequence_id);
	}
}
/* =============================================================== */
bool TWIPR_Sequencer::loadSequence(
		twipr_sequencer_sequence_data_t sequence_data) {

	info("Load sequence %d with length %d", sequence_data.sequence_id,
			sequence_data.length);

	this->loaded_sequence = sequence_data;
	this->_sequence_received = false;

	if (sequence_data.length > TWIPR_SEQUENCE_BUFFER_SIZE) {
		warning("Sequence %d too long: %d samples (%d max)",
				sequence_data.sequence_id, sequence_data.length,
				TWIPR_SEQUENCE_BUFFER_SIZE);
		return false;
	}

	this->config.comm->receiveTrajectoryInputs(sequence_data.length);
	return true;
}

/* =============================================================== */
twipr_sequencer_sequence_data_t TWIPR_Sequencer::readSequence() {
	return this->loaded_sequence;
}
/* =============================================================== */
void TWIPR_Sequencer::resetSequenceData() {

}

/* =============================================================== */
twipr_sequencer_sample_t TWIPR_Sequencer::getSample() {
	twipr_sequencer_sample_t sample;

	if (this->mode == TWIPR_SEQUENCER_MODE_RUNNING) {
		sample.sequence_id = this->loaded_sequence.sequence_id;
		sample.sequence_tick = this->sequence_tick;
	} else {
		sample.sequence_id = 0;
		sample.sequence_tick = 0;
	}

	return sample;
}

/* =============================================================== */
void TWIPR_Sequencer::spiSequenceReceived_callback(uint16_t trajectory_length) {
	// Copy the trajectory into the buffer
	memcpy((uint8_t*) this->buffer, (uint8_t*) this->rx_buffer,
			sizeof(twipr_sequence_input_t) * TWIPR_SEQUENCE_BUFFER_SIZE);

	this->_sequence_received = true;
	info("Received trajectory");
}

/* =============================================================== */
void TWIPR_Sequencer::modeChange_callback(twipr_control_mode_t mode) {
	// TODO
	if (this->mode != TWIPR_SEQUENCER_MODE_RUNNING) {
		return;
	}

}
