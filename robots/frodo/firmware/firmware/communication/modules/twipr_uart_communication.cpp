///*
// * twipr_communication.cpp
// *
// *  Created on: Feb 22, 2023
// *      Author: lehmann_workstation
// */
//
#include "twipr_uart_communication.h"
#include "robot-control_std.h"

static core_comm_UartInterface_config_t twipr_communication_uart_cm4_interface_config =
		{ .uart = { .mode = CORE_HARDWARE_UART_MODE_DMA, .cobs_encode_rx = 1,
				.cobs_encode_tx = 1, .queues = 1, }, .use_protocol = 1,
				.use_queue = 1 };

static const osThreadAttr_t task_attributes = { .name = "twipr_uart_comm_task",
		.stack_size = 512 * 4, .priority = (osPriority_t) osPriorityNormal };

static core_comm_SerialMessage_memory<128> incoming_msg;
static core_comm_SerialMessage_memory<128> outgoing_msg;

bool rx_available = false;

/* =========================================================================== */
void twipr_uart_comm_task(void *argument) {

	TWIPR_UART_Communication *comm = (TWIPR_UART_Communication*) argument;
	comm->task = xTaskGetCurrentTaskHandle();
	comm->taskFunction();
}

/* =========================================================================== */
TWIPR_UART_Communication::TWIPR_UART_Communication() {

}

/* =========================================================================== */
void TWIPR_UART_Communication::init(twipr_uart_comm_config_t config) {

	// Initialize the UART interface to the Raspberry Pi
	this->_uart_cm4.init(config.huart,
			twipr_communication_uart_cm4_interface_config);

	this->_uart_cm4.registerCallback(CORE_COMM_SERIAL_SOCKET_CB_RX,
			core_utils_Callback<void, void>(this,
					&TWIPR_UART_Communication::_rx_callback));
}

/* =========================================================================== */
void TWIPR_UART_Communication::start() {

	// Start the UART interfaces
	this->_uart_cm4.start();

	// Start the task
	this->_thread = osThreadNew(twipr_uart_comm_task, this, &task_attributes);
}
/* =========================================================================== */
void TWIPR_UART_Communication::reset(){
	this->_uart_cm4.reset();
}
/* =========================================================================== */
void TWIPR_UART_Communication::send(uint8_t cmd, uint8_t module,
		uint16_t address, uint8_t flag, uint8_t *data, uint8_t len) {

	outgoing_msg.cmd = cmd;
	outgoing_msg.address_1 = module;
	outgoing_msg.address_2 = address >> 8;
	outgoing_msg.address_3 = address;
	outgoing_msg.flag = flag;

	for (int i = 0; i < len; i++) {
		outgoing_msg.data_ptr[i] = data[i];
	}
	outgoing_msg.len = len;
	this->send(&outgoing_msg);
}

/* =========================================================================== */
void TWIPR_UART_Communication::send(core_comm_SerialMessage *msg) {

	// Check the message
	this->_uart_cm4.send(msg);
}

/* =========================================================================== */
void TWIPR_UART_Communication::registerCallback(
		twipr_uart_comm_callback_id_t callback_id,
		core_utils_Callback<void, core_comm_SerialMessage*> callback) {
	switch (callback_id) {
	case TWIPR_UART_COMM_CALLBACK_RX_MSG: {
		this->_callbacks.rx_msg = callback;
		break;
	}
	case TWIPR_UART_COMM_CALLBACK_MSG_WRITE: {
		this->_callbacks.write_msg = callback;
		break;
	}
	case TWIPR_UART_COMM_CALLBACK_MSG_READ: {
		this->_callbacks.read_msg = callback;
		break;
	}
	case TWIPR_UART_COMM_CALLBACK_MSG_FUNC: {
		this->_callbacks.func_msg = callback;
		break;
	}
	}

}

/* =========================================================================== */
void TWIPR_UART_Communication::taskFunction() {
	//	uint32_t kernel_ticks = 0;
	while (true) {
		if (rx_available){
			rx_available = false;
			if (this->_uart_cm4.rx_queue.available()) {
						this->_handleIncomingMessages();
			}
		}
		osDelay(1);
//		ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

	}
}

/* =========================================================================== */
void TWIPR_UART_Communication::_handleIncomingMessages() {
	// Loop through all the messages in the rx queue
	while (this->_uart_cm4.rx_queue.available()) {
		this->_uart_cm4.rx_queue.read(&incoming_msg);

		// Check if the message is correct
		// TODO

		// Handle the different addresses

		// Handle the different commands
		switch (incoming_msg.cmd) {
		case MSG_COMMAND_WRITE: {
//			this->_handleMessage_write(&incoming_msg);
			if (this->_callbacks.write_msg.registered) {
				this->_callbacks.write_msg.call(&incoming_msg);
			}
			break;
		}
		case MSG_COMMAND_READ: {
			if (this->_callbacks.read_msg.registered) {
				this->_callbacks.read_msg.call(&incoming_msg);
			}
//			this->_handleMessage_read(&incoming_msg);
			break;
		}
		case MSG_COMMAND_EVENT: {
			nop();
			break;
		}
		case MSG_COMMAND_MSG: {
			nop();
			break;
		}
		case MSG_COMMAND_FCT: {
			if (this->_callbacks.func_msg.registered) {
				this->_callbacks.func_msg.call(&incoming_msg);
			}
//			this->_handleMessage_function(&incoming_msg);
			break;
		}
		case MSG_COMMAND_ECHO: {
			this->send(&incoming_msg);
			break;
		}
		default: {
			continue;
			break;
		}
		}
		this->last_received_message_tick = osKernelGetTickCount();
	}
}

///* =========================================================================== */
//void TWIPR_UART_Communication::_handleMessage_function(
//		core_comm_SerialMessage *msg) {
//
//	// Check if the module is the default module
//	if (!msg->address_1 == 0x00) {
//		return; // TODO
//	}
//
//	// Check if the address exists in the register map and is a function
//	uint16_t address = uint8_to_uint16(msg->address_2, msg->address_3);
//
//	if (!this->register_map->hasEntry(address)) {
//		return;
//	}
//
//	// Check if it is a function
//	if (this->register_map->getType(address) != REGISTER_ENTRY_FUNCTION) {
//		return;
//	}
//
//	// Execute the function and store the data
//	uint8_t ret_size = this->register_map->execute(address, msg->data_ptr,
//			outgoing_msg.data_ptr);
//
//	// Send back a message if the function returns something
//	if (ret_size > 0) {
//		outgoing_msg.address_1 = msg->address_1;
//		outgoing_msg.address_2 = msg->address_2;
//		outgoing_msg.address_3 = msg->address_3;
//		outgoing_msg.flag = 1;
//		outgoing_msg.cmd = MSG_COMMAND_ANSWER;
//		outgoing_msg.len = ret_size;
//		this->send(&outgoing_msg);
//	}
//}

/* =========================================================================== */
void TWIPR_UART_Communication::_rx_callback() {
	rx_available = true;
//	if (this->task != NULL) {
//		xTaskNotifyGive(this->task);
//	}
}
