/*
 * core_debug.hpp
 *
 *  Created on: 16 Feb 2023
 *      Author: lehmann_workstation
 */

#ifndef UTILS_CORE_DEBUG_HPP_
#define UTILS_CORE_DEBUG_HPP_

#include <communication/uart_interface/core_comm_UartInterface.h>
#include "../hardware/UART/core_hardware_UART.h"

typedef enum debug_interface_type {
	CORE_DEBUG_INTERFACE_UART = 0,
	CORE_DEBUG_INTERFACE_USB = 1
} debug_interface_type ;

enum core_debug_CB_ID {
	CORE_DEBUG_CB_RX
};

class core_debug_Interface {
public:
	core_debug_Interface(debug_interface_type interface_type, UART_HandleTypeDef* huart);
	core_debug_Interface(debug_interface_type interface_type);

	void registerCallback(core_debug_CB_ID callback_id,
				void (*callback)(void *argument, void *params), void *params);

	void start();

	void print(uint8_t* buffer, uint16_t len);
	void println(uint8_t* buffer, uint16_t len);
	void println();
	void print(float number);
	void print(uint8_t number);
	void print(uint16_t number);

private:

	void write(uint8_t* buffer, uint16_t len);
	UART_HandleTypeDef* huart;
	core_comm_UartInterface<10, 128> uart_interface;
	debug_interface_type type;

	void rx_callback();
};


void uart_rx_callback(void *argument, void* params);


void print(const char* buffer, uint16_t len);
void print(uint8_t* buffer, uint16_t len);
void println(const char *buffer, uint16_t len);
void println(uint8_t* buffer, uint16_t len);
void println();
void print(float number);
void print(uint8_t number);
void print(uint16_t number);



#endif /* UTILS_CORE_DEBUG_HPP_ */
