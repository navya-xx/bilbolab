/*
 * twipr_communication.cpp
 *
 *  Created on: 12 Mar 2023
 *      Author: Dustin Lehmann
 */

#include "twipr_communication.h"
#include <cstdio> // For sprintf
#include <cstring> // For strlen
#include <cstdarg> // For va_list, va_start, va_end

core_utils_RegisterMap<255> register_map = core_utils_RegisterMap<255>(
TWIPR_REGISTER_MAP_GENERAL);
;

static core_comm_SerialMessage outgoing_msg;

void sample_dma_transfer_cmplt_callback(DMA_HandleTypeDef *hdma);

TWIPR_CommunicationManager *active_manager = NULL;

TWIPR_CommunicationManager::TWIPR_CommunicationManager() {

}

/* ====================================================================== */
void TWIPR_CommunicationManager::init(twipr_communication_config_t config) {
	this->config = config;

	active_manager = this;

	// Initialize the UART CM4 Interface
	twipr_uart_comm_config_t uart_config = { .huart = this->config.huart };
	this->uart_interface.init(uart_config);

	this->uart_interface.registerCallback(TWIPR_UART_COMM_CALLBACK_MSG_WRITE,
			core_utils_Callback<void, core_comm_SerialMessage*>(this,
					&TWIPR_CommunicationManager::_uart_handleMsg_write_callback));

	this->uart_interface.registerCallback(TWIPR_UART_COMM_CALLBACK_MSG_READ,
			core_utils_Callback<void, core_comm_SerialMessage*>(this,
					&TWIPR_CommunicationManager::_uart_handleMsg_read_callback));

	this->uart_interface.registerCallback(TWIPR_UART_COMM_CALLBACK_MSG_FUNC,
			core_utils_Callback<void, core_comm_SerialMessage*>(this,
					&TWIPR_CommunicationManager::_uart_handleMsg_func_callback));

	core_utils_gpio_registerExtiCallback(this->config.reset_uart_exti,
			core_utils_Callback<void, void>(this,
					&TWIPR_CommunicationManager::resetUART));

	// Initialize the SPI Interface
	twipr_spi_comm_config_t spi_config = { .hspi = this->config.hspi,
			.sample_buffer = this->_sample_buffer_tx, .len_sample_buffer =
			TWIPR_FIRMWARE_SAMPLE_BUFFER_SIZE, .sequence_buffer =
					this->config.sequence_rx_buffer, .len_sequence_buffer =
					this->config.len_sequence_buffer };
	this->spi_interface.init(spi_config);

	this->spi_interface.registerCallback(TWIPR_SPI_COMM_CALLBACK_TRAJECTORY_RX,
			core_utils_Callback<void, uint16_t>(this,
					&TWIPR_CommunicationManager::_spi_rxTrajectory_callback));
	this->spi_interface.registerCallback(TWIPR_SPI_COMM_CALLBACK_SAMPLE_TX,
			core_utils_Callback<void, uint16_t>(this,
					&TWIPR_CommunicationManager::_spi_txSamples_callback));

	HAL_DMA_RegisterCallback(TWIPR_FIRMWARE_SAMPLE_DMA_STREAM,
			HAL_DMA_XFER_CPLT_CB_ID, sample_dma_transfer_cmplt_callback);

	// Initialize the CAN Bus
	can_config_t can_config = { .hfdcan = BOARD_FDCAN, };

	this->can.init(can_config);
}
/* ====================================================================== */
void TWIPR_CommunicationManager::start() {

	// Start the UART Interface
	this->uart_interface.start();

	// Start the SPI Interface
	this->spi_interface.start();

	// Start the CAN Bus
	this->can.start();
}
/* ====================================================================== */
void TWIPR_CommunicationManager::registerCallback(
		twipr_communication_callback_id_t callback_id,
		core_utils_Callback<void, uint16_t> callback) {
	switch (callback_id) {
	case TWIPR_COMM_CALLBACK_NEW_TRAJECTORY: {
		this->_callbacks.new_trajectory = callback;
	}
	}
}

/* ====================================================================== */
void TWIPR_CommunicationManager::resetUART() {
	this->uart_interface.reset();
}

/* ====================================================================== */
void TWIPR_CommunicationManager::_uart_handleMsg_write_callback(
		core_comm_SerialMessage *msg) {

	uint16_t address = uint8_to_uint16(msg->address_2, msg->address_3);

	if (!register_map.hasEntry(address)) {
		this->_uartResponseError(msg, TWIPR_COMM_ERROR_FLAG_WRONG_ADDRESS);
		return;
	}

	if (register_map.getType(address) != REGISTER_ENTRY_TYPE_WRITABLE
			&& register_map.getType(address)
					!= REGISTER_ENTRY_TYPE_READWRITEABLE) {
		this->_uartResponseError(msg, TWIPR_COMM_ERROR_FLAG_MSG_TYPE);
		return;
	}

	if (register_map.getInputSize(address) != msg->len) {
//		this->_uartResponseError(msg, TWIPR_COMM_ERROR_FLAG_LEN);
		return;
	}

	register_map.write(address, msg->data_ptr);

	outgoing_msg.address_1 = msg->address_1;
	outgoing_msg.address_1 = msg->address_2;
	outgoing_msg.address_1 = msg->address_3;
	outgoing_msg.cmd = MSG_COMMAND_ANSWER;
	outgoing_msg.flag = 1;
	outgoing_msg.len = 0;

//	this->uart_interface.send(&outgoing_msg);

}
/* ====================================================================== */
void TWIPR_CommunicationManager::_uart_handleMsg_read_callback(
		core_comm_SerialMessage *msg) {

	uint16_t address = uint8_to_uint16(msg->address_2, msg->address_3);

	if (!register_map.hasEntry(address)) {
		this->_uartResponseError(msg, TWIPR_COMM_ERROR_FLAG_WRONG_ADDRESS);
		return;
	}

	if (register_map.getType(address) != REGISTER_ENTRY_TYPE_READABLE
			&& register_map.getType(address)
					!= REGISTER_ENTRY_TYPE_READWRITEABLE) {
		this->_uartResponseError(msg, TWIPR_COMM_ERROR_FLAG_MSG_TYPE);
		return;
	}

	// Read the entry into the outgoing message
	uint16_t len = register_map.read(address, outgoing_msg.data_ptr);

	if (len > 0) {
		// Construct the outgoing message
		outgoing_msg.address_1 = msg->address_1;
		outgoing_msg.address_2 = msg->address_2;
		outgoing_msg.address_3 = msg->address_3;
		outgoing_msg.flag = 1;
		outgoing_msg.cmd = MSG_COMMAND_ANSWER;
		outgoing_msg.len = len;

		this->uart_interface.send(&outgoing_msg);
	}
}

/* ====================================================================== */
void TWIPR_CommunicationManager::_uart_handleMsg_func_callback(
		core_comm_SerialMessage *msg) {

	uint16_t address = uint8_to_uint16(msg->address_2, msg->address_3);

	if (!register_map.hasEntry(address)) {
		this->_uartResponseError(msg, TWIPR_COMM_ERROR_FLAG_WRONG_ADDRESS);
		return;
	}

	if (register_map.getInputSize(address) != msg->len) {
		this->_uartResponseError(msg, TWIPR_COMM_ERROR_FLAG_LEN);
		return;
	}

	if (register_map.getType(address) != REGISTER_ENTRY_TYPE_EXECUTABLE) {
		this->_uartResponseError(msg, TWIPR_COMM_ERROR_FLAG_MSG_TYPE);
		return;
	}

	// Execute the function and store the data
	uint8_t ret_size = register_map.execute(address, msg->data_ptr,
			outgoing_msg.data_ptr);

	// Send back a message if the function returns something
	if (ret_size > 0) {
		outgoing_msg.address_1 = msg->address_1;
		outgoing_msg.address_2 = msg->address_2;
		outgoing_msg.address_3 = msg->address_3;
		outgoing_msg.flag = 1;
		outgoing_msg.cmd = MSG_COMMAND_ANSWER;
		outgoing_msg.len = ret_size;
		this->uart_interface.send(&outgoing_msg);
	}
}

/* ====================================================================== */
void TWIPR_CommunicationManager::_uartResponseError(
		core_comm_SerialMessage *incoming_message, uint8_t error_code) {
	outgoing_msg.address_1 = incoming_message->address_1;
	outgoing_msg.address_2 = incoming_message->address_2;
	outgoing_msg.address_3 = incoming_message->address_3;
	outgoing_msg.cmd = MSG_COMMAND_ANSWER;
	outgoing_msg.flag = 0;
	outgoing_msg.len = 1;
	outgoing_msg.data_ptr[0] = error_code;
	this->uart_interface.send(&outgoing_msg);
}
/* ====================================================================== */
void TWIPR_CommunicationManager::_spi_rxTrajectory_callback(uint16_t len) {
	// We have received a new trajectory by the CM4
	if (this->_callbacks.new_trajectory.registered) {
		this->_callbacks.new_trajectory.call(len);
	}
	this->spi_interface.provideSampleData();
}
/* ====================================================================== */
void TWIPR_CommunicationManager::sampleBufferDMATransfer_callback() {
	this->spi_interface.stopTransmission();
	this->spi_interface.provideSampleData();
	this->config.notification_gpio_tx.toggle();
}
/* ====================================================================== */
void TWIPR_CommunicationManager::_spi_txSamples_callback(uint16_t len) {
//	this->config.notification_gpio_tx.write(0);
}

/* ====================================================================== */
void TWIPR_CommunicationManager::receiveTrajectory() {
	this->spi_interface.stopTransmission();
	this->spi_interface.receiveTrajectory();
}

/* ====================================================================== */
void TWIPR_CommunicationManager::provideSampleData(
		twipr_logging_sample_t *buffer) {
	HAL_DMA_Start_IT(TWIPR_FIRMWARE_SAMPLE_DMA_STREAM, (uint32_t) buffer,
			(uint32_t) &this->_sample_buffer_tx,
			TWIPR_FIRMWARE_SAMPLE_BUFFER_SIZE * sizeof(twipr_logging_sample_t));
}

/* ======================================================================*/
void sample_dma_transfer_cmplt_callback(DMA_HandleTypeDef *hdma) {
	active_manager->sampleBufferDMATransfer_callback();
}

/* ======================================================================*/
void TWIPR_CommunicationManager::sendMessage(BILBO_Message_t &message) {
	core_comm_SerialMessage serial_msg = message.encode();
	// some uart sending stuff
	this->uart_interface.send(&serial_msg);
}

/* ======================================================================*/
void TWIPR_CommunicationManager::debugPrint(const char *text) {
	if (text) {
		size_t length = strlen(text);
		if (length < DEBUG_PRINT_BUFFER_SIZE) {
			// Copy message to the tx_buffer
			strncpy(this->_debug_message.data->message, text, length);
			this->_debug_message.data->message[length] = '\0'; // Ensure null-termination
			this->_debug_message.data->flag = 0;
			this->sendMessage(this->_debug_message);
		}
	}
}
/* ======================================================================*/
void TWIPR_CommunicationManager::debugPrintf(const char *format, ...) {
	va_list args;
	va_start(args, format);

	// Format the string into tx_buffer
	int length = vsnprintf(this->_debug_message.data->message,
			DEBUG_PRINT_BUFFER_SIZE, format, args);
	va_end(args);

	this->_debug_message.data->flag = 0;

	if (length > 0 && length < DEBUG_PRINT_BUFFER_SIZE) {
		this->sendMessage(this->_debug_message);
	}

}

/* ======================================================================*/
void TWIPR_CommunicationManager::debugWarning(const char *text) {
	if (text) {
		size_t length = strlen(text);
		if (length < DEBUG_PRINT_BUFFER_SIZE) {
			// Copy message to the tx_buffer
			strncpy(this->_debug_message.data->message, text, length);
			this->_debug_message.data->message[length] = '\0'; // Ensure null-termination
			this->_debug_message.data->flag = 1;
			this->sendMessage(this->_debug_message);
		}
	}
}
/* ======================================================================*/
void TWIPR_CommunicationManager::debugWarning(const char *format, ...) {
	va_list args;
	va_start(args, format);

	// Format the string into tx_buffer
	int length = vsnprintf(this->_debug_message.data->message,
			DEBUG_PRINT_BUFFER_SIZE, format, args);
	va_end(args);

	this->_debug_message.data->flag = 1;

	if (length > 0 && length < DEBUG_PRINT_BUFFER_SIZE) {
		this->sendMessage(this->_debug_message);
	}
}
