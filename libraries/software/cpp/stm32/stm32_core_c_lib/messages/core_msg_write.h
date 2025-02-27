/*
 * core_msg_write.h
 *
 *  Created on: Jun 27, 2022
 *      Author: Dustin Lehmann
 */

#ifndef MESSAGES_CORE_MSG_WRITE_H_
#define MESSAGES_CORE_MSG_WRITE_H_

#include "core_messages.h"

// WRITE
//#define MSG_STM32_CORE_WRITE_Register 0x01
//#define MSG_STM32_CORE_WRITE_Debug 0x02
//
//#define CORE_MSG_WRITE_ID_Led 0x03
//#define CORE_MSG_WRITE_LEN_Led 2
//
////#define MSG_STM32_CORE_WRITE_Led 0x04
//#define MSG_STM32_CORE_WRITE_StatusLed 0x05
//#define MSG_STM32_CORE_WRITE_ExternalPower 0x06
//#define MSG_STM32_CORE_WRITE_Buzzer 0x07
//#define MSG_STM32_CORE_WRITE_Eeprom 0x08
//#define MSG_STM32_CORE_WRITE_Flash 0x09
//
//// REQUEST
//
//#define MSG_STM32_CORE_REQ_Register 0x01
//
//// ANSWER
//#define MSG_STM32_CORE_ANSWER_Register 0x01

#define MSG_CORE_WRITE_Led_ID 0x03
#define MSG_CORE_WRITE_Led_LEN 2

void core_msg_write_rxHandler(core_comm_Message_t *msg);

void core_msg_core_write_led_rxHandler(core_comm_Message_t *msg);

#endif /* MESSAGES_CORE_MSG_WRITE_H_ */
