/*
 * twipr_communication.h
 *
 *  Created on: 12 Mar 2023
 *      Author: Dustin Lehmann
 */

#ifndef COMMUNICATION_TWIPR_COMMUNICATION_H_
#define COMMUNICATION_TWIPR_COMMUNICATION_H_

#include "core.h"
#include "twipr_uart_communication.h"
#include "twipr_spi_communication.h"
#include "firmware_defs.h"
#include "twipr_control.h"
#include "twipr_sequencer.h"

#include "twipr_messages.h"

#define TWIPR_COMM_ERROR_FLAG_UNKNOWN 0x01
#define TWIPR_COMM_ERROR_FLAG_WRONG_ADDRESS 0x02
#define TWIPR_COMM_ERROR_FLAG_WRITE 0x03
#define TWIPR_COMM_ERROR_FLAG_READ 0x04
#define TWIPR_COMM_ERROR_FLAG_LEN 0x05
#define TWIPR_COMM_ERROR_FLAG_MSG_TYPE 0x06

extern core_utils_RegisterMap<255> register_map;

typedef enum twipr_communication_callback_id_t {
	TWIPR_COMM_CALLBACK_NEW_TRAJECTORY,
} twipr_communication_callback_id_t;

typedef struct twipr_communication_callbacks_t {
	core_utils_Callback<void, uint16_t> new_trajectory;
} twipr_communication_callbacks_t;


#define DEBUG_PRINT_BUFFER_SIZE 128

typedef struct debug_message_data_t {
	uint8_t flag;
	char message [DEBUG_PRINT_BUFFER_SIZE];
} debug_message_data_t;

typedef BILBO_Message<debug_message_data_t, MSG_EVENT, MESSAGE_ID_DEBUG> BILBO_Debug_Message;

typedef struct twipr_communication_config_t {
	UART_HandleTypeDef *huart;
	SPI_HandleTypeDef *hspi;
	core_utils_GPIO notification_gpio_tx;
	twipr_sequence_input_t *sequence_rx_buffer;
	uint16_t len_sequence_buffer;
	uint16_t reset_uart_exti;
} twipr_communication_config_t;

class TWIPR_CommunicationManager {
public:
	TWIPR_CommunicationManager();

	void init(twipr_communication_config_t config);
	void start();

	void registerCallback(twipr_communication_callback_id_t callback_id,
			core_utils_Callback<void, uint16_t> callback);

	void provideSampleData(twipr_logging_sample_t *buffer);
	void receiveTrajectory();
	void resetUART();

	void sendMessage(BILBO_Message_t &message);

	void debugPrint(const char* text);
	void debugPrintf(const char* format, ...);
	void debugWarning(const char* text);
	void debugWarning(const char* format, ...);

	void sampleBufferDMATransfer_callback();

	twipr_communication_config_t config;
	TWIPR_UART_Communication uart_interface;
	TWIPR_SPI_Communication spi_interface;
	CAN can;

private:

	twipr_communication_callbacks_t _callbacks;

	void _uart_handleMsg_write_callback(core_comm_SerialMessage *msg);
	void _uart_handleMsg_read_callback(core_comm_SerialMessage *msg);
	void _uart_handleMsg_func_callback(core_comm_SerialMessage *msg);

	void _spi_rxTrajectory_callback(uint16_t len);
	void _spi_txSamples_callback(uint16_t len);

	void _uartResponseError(core_comm_SerialMessage *incoming_message,
			uint8_t error_code);

	twipr_logging_sample_t _sample_buffer_tx[TWIPR_FIRMWARE_SAMPLE_BUFFER_SIZE];

	BILBO_Debug_Message _debug_message;
};





#endif /* COMMUNICATION_TWIPR_COMMUNICATION_H_ */
