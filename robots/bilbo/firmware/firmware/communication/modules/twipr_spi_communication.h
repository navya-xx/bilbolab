/*
 * twipr_spi_communication.h
 *
 *  Created on: 12 Mar 2023
 *      Author: Dustin Lehmann
 */

#ifndef COMMUNICATION_TWIPR_SPI_COMMUNICATION_H_
#define COMMUNICATION_TWIPR_SPI_COMMUNICATION_H_

#include "core.h"
#include "twipr_logging.h"
#include "twipr_sequencer.h"

#define TWIPR_SPI_COMMAND_MESSAGE_LENGTH 4

typedef struct twipr_spi_comm_config_t {
	SPI_HandleTypeDef *hspi;
	twipr_logging_sample_t *sample_buffer;
	uint16_t len_sample_buffer;
	twipr_sequence_input_t *sequence_buffer;
	uint16_t len_sequence_buffer;
} twipr_spi_comm_config_t;

typedef enum twipr_spi_comm_mode_t {
	TWIPR_SPI_COMM_MODE_NONE = 0,
	TWIPR_SPI_COMM_MODE_RX = 1,
	TWIPR_SPI_COMM_MODE_TX = 2,
} twipr_spi_comm_mode_t;

typedef enum twipr_spi_comm_callback_id_t {
	TWIPR_SPI_COMM_CALLBACK_TRAJECTORY_RX, TWIPR_SPI_COMM_CALLBACK_SAMPLE_TX,
} twipr_spi_comm_callback_id_t;

typedef struct twipr_spi_comm_callbacks_t {
	core_utils_Callback<void, uint16_t> trajectory_rx_callback;
	core_utils_Callback<void, uint16_t> sample_tx_callback;
} twipr_spi_comm_callbacks_t;

class TWIPR_SPI_Communication {
public:
	TWIPR_SPI_Communication();
	void init(twipr_spi_comm_config_t config);
	void start();

//	void registerCallback(twipr_spi_comm_callback_id_t callback_id,
//			core_utils_Callback<void, void> callback);

	void registerCallback(twipr_spi_comm_callback_id_t callback_id,
			core_utils_Callback<void, uint16_t> callback);


	void stopTransmission();

	void receiveTrajectory();
	void provideSampleData();


	void receiveTrajectory(uint16_t len);
	void receiveTrajectory(twipr_sequence_input_t *trajectory_buffer,
			uint16_t len);
	void provideSampleData(uint16_t len);
	void provideSampleData(twipr_logging_sample_t *sample_buffer, uint16_t len);

	void rx_cmplt_function();
	void tx_cmplt_function();
	void rxtx_cmplt_function();

	twipr_spi_comm_config_t config;
	twipr_spi_comm_mode_t mode = TWIPR_SPI_COMM_MODE_NONE;
private:

	uint8_t _commandBuffer[TWIPR_SPI_COMMAND_MESSAGE_LENGTH];
	uint16_t _len;
	core_hardware_SPI_slave spi_slave;
	twipr_spi_comm_callbacks_t callbacks;
};

#endif /* COMMUNICATION_TWIPR_SPI_COMMUNICATION_H_ */

