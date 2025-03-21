/*
 * ModbusConfig.h
 *
 *  Created on: Apr 28, 2021
 *      Author: Alejandro Mera
 *
 *  This is a template for the Modbus library configuration.
 *  Every project needs a tailored copy of this file renamed to ModbusConfig.h, and added to the include path.
 */

#ifndef THIRD_PARTY_MODBUS_LIB_CONFIG_MODBUSCONFIG_H_
#define THIRD_PARTY_MODBUS_LIB_CONFIG_MODBUSCONFIG_H_



/* Uncomment the following line to enable support for Modbus RTU over USB CDC profile. Only tested for BluePill f103 board. */
//#define ENABLE_USB_CDC 1

/* Uncomment the following line to enable support for Modbus TCP. Only tested for Nucleo144-F429ZI. */
//#define ENABLE_TCP 1

/* Uncomment the following line to enable support for Modbus RTU USART DMA mode. Only tested for Nucleo144-F429ZI.  */
//#define ENABLE_USART_DMA 1


#define T35  1            // Timer T35 period (in ticks) for end frame detection.
#define MAX_BUFFER  127	    // Maximum size for the communication buffer in bytes.
#define TIMEOUT_MODBUS 1 // Timeout for master query (in ticks)
#define MAX_M_HANDLERS 1   //Maximum number of modbus handlers that can work concurrently
#define MAX_TELEGRAMS 40     //Max number of Telegrams in master queue
#define MODBUS_BUFFER_SIZE 127


#endif /* THIRD_PARTY_MODBUS_LIB_CONFIG_MODBUSCONFIG_H_ */
