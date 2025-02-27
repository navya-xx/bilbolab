/*
 * core_comm_signals.h
 *
 *  Created on: 19 Apr 2022
 *      Author: Dustin Lehmann
 */

#ifndef COMMUNICATION_CORE_COMM_SIGNALS_H_
#define COMMUNICATION_CORE_COMM_SIGNALS_H_

/* ======================================================================================= */
/* === Discrete Communication Signals === */
typedef enum {
	poll = 0, interrupt = 1
} core_comm_signal_type_t;

typedef enum {
	input = 1, output = 2
} core_comm_signal_direction_t;

typedef enum {
	reset = 0, set = 1
} core_comm_signal_state_t;

typedef struct {
	GPIO_TypeDef *gpio_port;
	uint16_t gpio_pin;
	core_comm_signal_type_t type;
	core_comm_signal_direction_t direction;
	core_comm_signal_state_t state;
	void (*callback_function);
} core_comm_signal_t;

uint8_t core_comm_signal_Init(core_comm_signal_t *signal);

uint8_t core_comm_signal_Read(core_comm_signal_t *signal);
uint8_t core_comm_signal_Set(core_comm_signal_t *signal, uint8_t state);
uint8_t core_comm_signal_Toggle(core_comm_signal_t *signal);
uint8_t core_comm_signal_SetInterrupt(core_comm_signal_t *signal,
		void (*callback));

#endif /* COMMUNICATION_CORE_COMM_SIGNALS_H_ */
