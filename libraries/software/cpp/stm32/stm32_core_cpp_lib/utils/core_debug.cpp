/*
 * core_debug.cpp
 *
 *  Created on: 16 Feb 2023
 *      Author: lehmann_workstation
 */

#include "core_debug.hpp"

core_debug_Interface *active_interface = NULL;

core_comm_UartInterface_config_t uart_config = { .uart = { .mode =
		CORE_HARDWARE_UART_MODE_DMA, .cobs_encode_rx = 0, .cobs_encode_tx = 0,
		.queues = 1 }, .use_protocol = 0, .use_queue = 0 };

/* ============================================================================= */
core_debug_Interface::core_debug_Interface(debug_interface_type interface_type,
		UART_HandleTypeDef *huart) {

	active_interface = this;
	this->type = interface_type;
	this->huart = huart;

	// Initialize the UART interface
	this->uart_interface.init(huart, uart_config);

	// Register Callback for Receiving
//	this->uart_interface.registerCallback(CORE_COMM_SERIAL_SOCKET_CB_RX,
//			uart_rx_callback, NULL);
}

/* ============================================================================= */
void core_debug_Interface::registerCallback(core_debug_CB_ID callback_id,
		void (*callback)(void *argument, void *params), void *params) {

}

/* ============================================================================= */
void core_debug_Interface::start() {
	if (this->type == CORE_DEBUG_INTERFACE_UART) {
		this->uart_interface.start();
	}
}

/* ============================================================================= */
void core_debug_Interface::write(uint8_t *buffer, uint16_t len) {
	if (this->type == CORE_DEBUG_INTERFACE_UART) {
		if (this->uart_interface.status != CORE_COMM_SERIAL_SOCKET_STATE_RUN) {
			return; // TODO: We should put the stuff into a buffer here
		} else {
			this->uart_interface.send(buffer, len);
		}
	} else if (this->type == CORE_DEBUG_INTERFACE_USB) {
		// TODO
	}
}

/* ============================================================================= */
void core_debug_Interface::print(uint8_t *buffer, uint16_t len) {
	this->write(buffer, len);
}
/* ============================================================================= */
void core_debug_Interface::println(uint8_t *buffer, uint16_t len) {
	this->write(buffer, len);
	this->println();
}
/* ============================================================================= */
void core_debug_Interface::println() {
	uint8_t data[] = "\n";
	this->write(data, 1);
}
/* ============================================================================= */
void core_debug_Interface::print(float number) {

}
/* ============================================================================= */
void core_debug_Interface::print(uint8_t number) {

}
/* ============================================================================= */
void core_debug_Interface::print(uint16_t number) {

}

//void uart_rx_callback(void *argument, void *params) {
//	core_utils_Buffer *buffer = (core_utils_Buffer*) argument;
//
//	nop();
//}

/* ============================================================================= */
void print(const char *buffer, uint16_t len) {
	if (active_interface != NULL) {
		active_interface->print((uint8_t*) buffer, len);
	}
}

void print(uint8_t *buffer, uint16_t len) {
	if (active_interface != NULL) {
		active_interface->print(buffer, len);
	}
}
void println(const char *buffer, uint16_t len) {
	if (active_interface != NULL) {
		active_interface->println((uint8_t*) buffer, len);
	}
}

void println(uint8_t *buffer, uint16_t len) {
	if (active_interface != NULL) {
		active_interface->println(buffer, len);
	}
}
void println() {
	if (active_interface != NULL) {
		active_interface->println();
	}
}
void print(float number) {

}
void print(uint8_t number) {

}
void print(uint16_t number) {

}
