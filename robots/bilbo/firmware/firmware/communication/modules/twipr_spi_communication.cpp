/*
 * twipr_spi_communication.cpp
 *
 *  Created on: 12 Mar 2023
 *      Author: Dustin Lehmann
 *
 *  Description:
 *      This file implements the SPI communication interface for TWIPR.
 *      It initializes the SPI slave interface, registers callbacks for
 *      RX/TX events, and provides functions for sending sample data and
 *      receiving trajectory inputs.
 */

#include "twipr_spi_communication.h"

/**
 * @brief Constructor for the TWIPR_SPI_Communication class.
 *
 * Currently, no additional initialization is performed in the constructor.
 */
TWIPR_SPI_Communication::TWIPR_SPI_Communication() {
}

/**
 * @brief Initialize the SPI communication interface.
 *
 * Configures the SPI hardware using the provided configuration structure.
 * It sets up the receive and transmit buffers, and registers callbacks for
 * RX (receive complete) and TX (transmit complete) events.
 *
 * @param config Configuration structure for SPI communication.
 */
void TWIPR_SPI_Communication::init(twipr_spi_comm_config_t config) {
    // Store the provided configuration locally.
    this->config = config;

    // Create a hardware SPI configuration structure and initialize buffers.
    core_hardware_spi_config_t spi_config = {
        .hspi = this->config.hspi,
        .rx_buffer = (uint8_t*) this->config.sequence_buffer,
        .tx_buffer = (uint8_t*) this->config.sample_buffer,
    };

    // Initialize the SPI slave with the configuration.
    this->spi_slave.init(spi_config);

    // Register the receive complete callback.
    this->spi_slave.registerCallback(
        CORE_HARDWARE_SPI_CALLBACK_RX,
        core_utils_Callback<void, void>(this, &TWIPR_SPI_Communication::rx_cmplt_function)
    );

    // Register the transmit complete callback.
    this->spi_slave.registerCallback(
        CORE_HARDWARE_SPI_CALLBACK_TX,
        core_utils_Callback<void, void>(this, &TWIPR_SPI_Communication::tx_cmplt_function)
    );

    // The RXTX callback and command buffer settings are currently commented out.
    // Uncomment and configure if full-duplex command processing is required.
    // this->spi_slave.registerCallback(CORE_HARDWARE_SPI_CALLBACK_RXTX,
    //     core_utils_Callback<void, void>(this, &TWIPR_SPI_Communication::rxtx_cmplt_function));
    //
    // uint8_t trajectory_size = sizeof(twipr_sequence_input_t);
    // uint8_t sample_size = sizeof(twipr_logging_sample_t);
    // tx_cmd_buf[1] = trajectory_size;
    // tx_cmd_buf[2] = sample_size;
}

/**
 * @brief Start the SPI communication interface.
 *
 * Starts the SPI slave interface and immediately provides sample data
 * for transmission.
 */
void TWIPR_SPI_Communication::start() {
    // Start the SPI slave.
    this->spi_slave.start();
    // Provide initial sample data for transmission.
    this->provideSampleData();
}

/**
 * @brief Register a callback for SPI communication events.
 *
 * This function allows registration of callbacks for either sample
 * transmission complete or trajectory reception events.
 *
 * @param callback_id Identifier for the callback type.
 * @param callback The callback function to be registered.
 */
void TWIPR_SPI_Communication::registerCallback(
    twipr_spi_comm_callback_id_t callback_id,
    core_utils_Callback<void, uint16_t> callback) {
    switch (callback_id) {
        case TWIPR_SPI_COMM_CALLBACK_SAMPLE_TX: {
            this->callbacks.sample_tx_callback = callback;
            break;
        }
        case TWIPR_SPI_COMM_CALLBACK_TRAJECTORY_RX: {
            this->callbacks.trajectory_rx_callback = callback;
            break;
        }
    }
}

/*
// The following function is commented out. It may be used in the future to
// listen for specific command messages over SPI.
// void TWIPR_SPI_Communication::listenForCommand() {
//     this->mode = TWIPR_SPI_COMM_MODE_NONE;
//     this->spi_slave.receiveTransmitData(this->_commandBuffer, tx_cmd_buf, TWIPR_SPI_COMMAND_MESSAGE_LENGTH);
// }
*/

/**
 * @brief Provide sample data using the default configuration.
 *
 * This function calls the overloaded provideSampleData function using the
 * default sample buffer and length provided in the configuration.
 */
void TWIPR_SPI_Communication::provideSampleData() {
    this->provideSampleData(this->config.sample_buffer, this->config.len_sample_buffer);
}

/**
 * @brief Receive trajectory inputs over SPI.
 *
 * Initiates the reception of trajectory input data into the configured sequence buffer.
 *
 * @param steps Number of trajectory steps (samples) to receive.
 */
void TWIPR_SPI_Communication::receiveTrajectoryInputs(uint16_t steps) {
    // Calculate the total size of the data to receive.
    this->spi_slave.receiveData(
        (uint8_t*) this->config.sequence_buffer,
        sizeof(twipr_sequence_input_t) * steps
    );
}

/**
 * @brief Provide sample data for transmission over SPI.
 *
 * Sets the communication mode to transmit and provides the sample data from
 * the given buffer with the specified length.
 *
 * @param sample_buffer Pointer to the sample data buffer.
 * @param len Number of samples to be transmitted.
 */
void TWIPR_SPI_Communication::provideSampleData(
    twipr_logging_sample_t *sample_buffer, uint16_t len) {

    // Set the communication mode to TX (transmit).
    this->mode = TWIPR_SPI_COMM_MODE_TX;
    // Provide the data to the SPI slave for transmission.
    this->spi_slave.provideData(
        (uint8_t*) sample_buffer,
        sizeof(twipr_logging_sample_t) * len
    );
}

/**
 * @brief SPI receive complete callback.
 *
 * This function is called when the SPI slave has completed receiving data.
 * If a trajectory reception callback is registered, it is invoked with the length
 * of the sequence buffer.
 */
void TWIPR_SPI_Communication::rx_cmplt_function() {
    if (this->callbacks.trajectory_rx_callback.registered) {
        // Pass the length of the sequence buffer to the registered callback.
        this->callbacks.trajectory_rx_callback.call(this->config.len_sequence_buffer);
    }
}

/**
 * @brief SPI transmit complete callback.
 *
 * This function is called when the SPI slave has finished transmitting data.
 * It invokes the sample transmission callback if registered, passing the length
 * of the transmitted data, and then immediately provides sample data for further transmission.
 */
void TWIPR_SPI_Communication::tx_cmplt_function() {
    // Execute the TX callback if one is registered.
    if (this->callbacks.sample_tx_callback.registered) {
        this->callbacks.sample_tx_callback.call(this->_len);
    }
    // Provide new sample data for continuous transmission.
    this->provideSampleData();
}

/**
 * @brief Stop the SPI transmission.
 *
 * Aborts any ongoing SPI transmission using the hardware SPI handle.
 */
void TWIPR_SPI_Communication::stopTransmission() {
    HAL_SPI_Abort(this->config.hspi);
}
