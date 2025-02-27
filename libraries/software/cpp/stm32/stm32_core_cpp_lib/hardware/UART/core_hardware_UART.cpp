/*
 * core_hardware_UART.cpp
 *
 *  Created on: Jul 7, 2022
 *      Author: Dustin Lehmann
 */

#include "core_hardware_UART.h"

#if CORE_CONFIG_USE_UART


UART *uarts[CORE_CONFIG_MAX_UARTS];
uint8_t num_uarts = 0;

core_hardware_UART_config core_hardware_uart_std_config = { .mode =
		CORE_HARDWARE_UART_MODE_DMA, .cobs_encode_rx = 1, .cobs_encode_tx = 1,
		.queues = 1, };


/* ============================================================================= */
void uartRxCmpltDMA_callback(UART_HandleTypeDef *huart, uint16_t size) {
	for (int i = 0; i < num_uarts; i++) {
		if (!(uarts[i] == NULL) && (uarts[i]->get_huart() == huart)) {
			uarts[i]->rxFunction(size);
		}
	}
}

#endif


void UART_Reset(UART_HandleTypeDef *huart)
{
    if (huart == NULL)
        return;

    // Disable the UART peripheral
    __HAL_UART_DISABLE(huart);

    // Reset UART peripheral (using the Reset and Clock Control Register)
    if (huart->Instance == USART1)
    {
        __HAL_RCC_USART1_FORCE_RESET();
        __HAL_RCC_USART1_RELEASE_RESET();
    }
    else if (huart->Instance == USART2)
    {
        __HAL_RCC_USART2_FORCE_RESET();
        __HAL_RCC_USART2_RELEASE_RESET();
    }
    else if (huart->Instance == USART3)
    {
        __HAL_RCC_USART3_FORCE_RESET();
        __HAL_RCC_USART3_RELEASE_RESET();
    }
    else if (huart->Instance == UART4)
    {
        __HAL_RCC_UART4_FORCE_RESET();
        __HAL_RCC_UART4_RELEASE_RESET();
    }
    else if (huart->Instance == UART5)
    {
        __HAL_RCC_UART5_FORCE_RESET();
        __HAL_RCC_UART5_RELEASE_RESET();
    }
    else if (huart->Instance == USART6)
    {
        __HAL_RCC_USART6_FORCE_RESET();
        __HAL_RCC_USART6_RELEASE_RESET();
    }
    else if (huart->Instance == UART7)
    {
        __HAL_RCC_UART7_FORCE_RESET();
        __HAL_RCC_UART7_RELEASE_RESET();
    }
    else if (huart->Instance == UART8)
    {
        __HAL_RCC_UART8_FORCE_RESET();
        __HAL_RCC_UART8_RELEASE_RESET();
    }
    else
    {
        // Unknown instance, handle error if needed
        return;
    }

    // Clear all flags in the Status Register
    __HAL_UART_CLEAR_FLAG(huart, UART_FLAG_RXNE | UART_FLAG_TC | UART_FLAG_TXE |
                                  UART_FLAG_IDLE | UART_FLAG_ORE | UART_FLAG_NE |
                                  UART_FLAG_FE | UART_FLAG_PE);

    // Re-enable the UART peripheral
    __HAL_UART_ENABLE(huart);

    // Reinitialize the UART (if necessary, reconfigure settings after reset)
    if (HAL_UART_Init(huart) != HAL_OK)
    {
        // Initialization Error
    	nop();
    }
}
