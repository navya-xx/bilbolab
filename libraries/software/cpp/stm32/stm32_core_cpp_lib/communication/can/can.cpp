/*
 * can.cpp
 *
 *  Created on: May 26, 2024
 *      Author: lehmann
 */

#include <cstring>
#include "can.h"

CAN *can;

uint32_t mapDLC(uint8_t dataLength);

CAN::CAN() {
    this->mapMutex = xSemaphoreCreateMutex(); // Use a mutex for task-level synchronization
}

CAN::~CAN() {
    xSemaphoreTake(this->mapMutex, portMAX_DELAY);
    for (int i = 0; i < CAN_NUMBER_RR; i++) {
        if (readRequests[i].isOpen) {
            // No need to delete task notifications
            readRequests[i].isOpen = false;
        }
    }
    xSemaphoreGive(this->mapMutex);
    vSemaphoreDelete(this->mapMutex);
}

HAL_StatusTypeDef CAN::init(can_config_t config) {
    HAL_StatusTypeDef status;
    can = this;
    this->config = config;

    // Initialize read requests
    for (int i = 0; i < CAN_NUMBER_RR; i++) {
        readRequests[i].id = 0;
        readRequests[i].taskHandle = nullptr;
        readRequests[i].isOpen = false;
    }

    for (int i = 0; i < CAN_NUMBER_CALLBACKS; i++) {
        standardIDCallbacks[i].FilterID1 = 0x000;
        standardIDCallbacks[i].FilterID2 = 0x7FF; // Default: match all 11-bit IDs
        standardIDCallbacks[i].callback.registered = false;

        extendedIDCallbacks[i].callback = nullptr;
        extendedIDCallbacks[i].FilterID1 = 0x00000000;
        extendedIDCallbacks[i].FilterID2 = 0x1FFFFFFF; // Default: match all 29-bit IDs
        extendedIDCallbacks[i].callback.registered = false;
    }

    // Configure filters (same as original)
    FDCAN_FilterTypeDef filterConfig;

    // Filter for 11-bit frames -> FIFO 1
    filterConfig.IdType = FDCAN_STANDARD_ID;
    filterConfig.FilterIndex = 0; // First filter
    filterConfig.FilterType = FDCAN_FILTER_RANGE;
    filterConfig.FilterConfig = FDCAN_FILTER_TO_RXFIFO1; // Route to FIFO 1
    filterConfig.FilterID1 = 0x000; // Match all 11-bit IDs (0x000 to 0x7FF)
    filterConfig.FilterID2 = 0x7FF;
    status = HAL_FDCAN_ConfigFilter(this->config.hfdcan, &filterConfig);
    if (status != HAL_OK) {
        return status;
    }

    // Filter for 29-bit frames -> FIFO 0
    filterConfig.IdType = FDCAN_EXTENDED_ID;
    filterConfig.FilterIndex = 1; // Second filter
    filterConfig.FilterType = FDCAN_FILTER_RANGE;
    filterConfig.FilterConfig = FDCAN_FILTER_TO_RXFIFO0; // Route to FIFO 0
    filterConfig.FilterID1 = 0x00000000; // Match all 29-bit IDs (0x00000000 to 0x1FFFFFFF)
    filterConfig.FilterID2 = 0x1FFFFFFF;
    status = HAL_FDCAN_ConfigFilter(this->config.hfdcan, &filterConfig);
    if (status != HAL_OK) {
        return status;
    }

    // Enable Notifications
    status = HAL_FDCAN_ActivateNotification(this->config.hfdcan,
        FDCAN_IT_RX_FIFO0_NEW_MESSAGE, 0);

    status = HAL_FDCAN_ActivateNotification(this->config.hfdcan,
        FDCAN_IT_RX_FIFO1_NEW_MESSAGE, 0);

    return status;
}

HAL_StatusTypeDef CAN::start() {
    return HAL_FDCAN_Start(this->config.hfdcan);
}

bool CAN::addReadRequest(uint32_t id, TaskHandle_t taskHandle) {
    xSemaphoreTake(this->mapMutex, portMAX_DELAY);
    for (int i = 0; i < CAN_NUMBER_RR; i++) {
        if (!readRequests[i].isOpen) {
            readRequests[i].id = id;
            readRequests[i].taskHandle = taskHandle;
            readRequests[i].isOpen = true;
            xSemaphoreGive(this->mapMutex);
            return true;
        }
    }
    xSemaphoreGive(this->mapMutex);
    return false;
}

void CAN::removeReadRequest(uint32_t id) {
    xSemaphoreTake(this->mapMutex, portMAX_DELAY);
    for (int i = 0; i < CAN_NUMBER_RR; i++) {
        if (readRequests[i].isOpen && readRequests[i].id == id) {
            readRequests[i].isOpen = false;
            readRequests[i].taskHandle = nullptr;
            break;
        }
    }
    xSemaphoreGive(this->mapMutex);
}

void CAN::onMessageReceived(const FDCAN_RxHeaderTypeDef &header, uint8_t *data) {
    BaseType_t higherPriorityTaskWoken = pdFALSE;

    // Check for matching read request
    for (int i = 0; i < CAN_NUMBER_RR; i++) {
        if (readRequests[i].isOpen && readRequests[i].id == header.Identifier) {
            uint8_t actualLength = (uint8_t) header.DataLength;

            // Store response data
            memcpy(readRequests[i].responseData, data, actualLength);
            readRequests[i].responseLength = actualLength;
            readRequests[i].isOpen = false;

            // Notify the task
            vTaskNotifyGiveFromISR(readRequests[i].taskHandle, &higherPriorityTaskWoken);
            portYIELD_FROM_ISR(higherPriorityTaskWoken);
            break;
        }
    }

    // Process callbacks (same as original)
    if (header.IdType == FDCAN_STANDARD_ID) {
        for (int i = 0; i < CAN_NUMBER_CALLBACKS; i++) {
            if (standardIDCallbacks[i].callback.registered &&
                header.Identifier >= standardIDCallbacks[i].FilterID1 &&
                header.Identifier <= standardIDCallbacks[i].FilterID2) {

                can_frame_callback_input_t callback_input = {
                    .id = header.Identifier,
                    .data = data,
                    .length = (uint8_t) header.DataLength
                };
                standardIDCallbacks[i].callback.call(callback_input);
            }
        }
    }

    if (header.IdType == FDCAN_EXTENDED_ID) {
        for (int i = 0; i < CAN_NUMBER_CALLBACKS; i++) {
            if (extendedIDCallbacks[i].callback.registered &&
                header.Identifier >= extendedIDCallbacks[i].FilterID1 &&
                header.Identifier <= extendedIDCallbacks[i].FilterID2) {

                can_frame_callback_input_t callback_input = {
                    .id = header.Identifier,
                    .data = data,
                    .length = (uint8_t) header.DataLength
                };
                extendedIDCallbacks[i].callback.call(callback_input);
            }
        }
    }
}

HAL_StatusTypeDef CAN::sendMessage(uint32_t id, uint8_t *data, uint8_t length, bool isExtendedID) {
    // Map the length
    uint32_t can_dlc = mapDLC(length);

    if (can_dlc == 0xFFFFFFFF) {
        return HAL_ERROR;
    }

    FDCAN_TxHeaderTypeDef TxHeader = {
        .Identifier = id,
        .IdType = isExtendedID ? FDCAN_EXTENDED_ID : FDCAN_STANDARD_ID,
        .TxFrameType = FDCAN_DATA_FRAME,
        .DataLength = can_dlc,
        .ErrorStateIndicator = FDCAN_ESI_ACTIVE,
        .BitRateSwitch = FDCAN_BRS_OFF,
        .FDFormat = FDCAN_CLASSIC_CAN,
        .TxEventFifoControl = FDCAN_NO_TX_EVENTS,
        .MessageMarker = 0
    };

    HAL_StatusTypeDef status = HAL_FDCAN_AddMessageToTxFifoQ(this->config.hfdcan, &TxHeader, data);

    if (status) {
        nop(); // Placeholder for additional logic if needed
    }

    return status;
}

CAN_Status CAN::sendRemoteFrame(uint32_t id, uint32_t timeoutMs,
    uint8_t *responseData, uint8_t requestLength, uint8_t &responseLength) {

    TaskHandle_t currentTask = xTaskGetCurrentTaskHandle();

    if (!addReadRequest(id, currentTask)) {
        return CAN_RR_FULL;
    }

    // Send Remote Frame
    FDCAN_TxHeaderTypeDef TxHeader = {
        .Identifier = id,
        .IdType = FDCAN_EXTENDED_ID,
        .TxFrameType = FDCAN_REMOTE_FRAME,
        .DataLength = mapDLC(requestLength),
        .ErrorStateIndicator = FDCAN_ESI_ACTIVE,
        .BitRateSwitch = FDCAN_BRS_OFF,
        .FDFormat = FDCAN_CLASSIC_CAN,
        .TxEventFifoControl = FDCAN_NO_TX_EVENTS,
        .MessageMarker = 0
    };

    if (HAL_FDCAN_AddMessageToTxFifoQ(this->config.hfdcan, &TxHeader, nullptr) != HAL_OK) {
        removeReadRequest(id);
        return CAN_READING_ERROR;
    }

    // Wait for response or timeout
    if (ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(timeoutMs)) > 0) {
        for (int i = 0; i < CAN_NUMBER_RR; i++) {
            if (readRequests[i].id == id && !readRequests[i].isOpen) {
                memcpy(responseData, readRequests[i].responseData, readRequests[i].responseLength);
                responseLength = readRequests[i].responseLength;
                break;
            }
        }
        removeReadRequest(id);
        return CAN_SUCCESS;
    } else {
        removeReadRequest(id);
        return CAN_READING_ERROR;
    }
}

/* ---------------------------------------------------------------------------- */
// IRQ Callback Integration for FIFO 0 (29-bit IDs)
extern "C" void HAL_FDCAN_RxFifo0Callback(FDCAN_HandleTypeDef *hfdcan,
		uint32_t RxFifo0ITs) {
	FDCAN_RxHeaderTypeDef rxHeader;
	uint8_t rxData[8];
	if (HAL_FDCAN_GetRxMessage(hfdcan, FDCAN_RX_FIFO0, &rxHeader, rxData)
			== HAL_OK) {
		can->onMessageReceived(rxHeader, rxData);
	}
}

// IRQ Callback Integration for FIFO 1 (11-bit IDs)
extern "C" void HAL_FDCAN_RxFifo1Callback(FDCAN_HandleTypeDef *hfdcan,
		uint32_t RxFifo1ITs) {
	FDCAN_RxHeaderTypeDef rxHeader;
	uint8_t rxData[8];
	if (HAL_FDCAN_GetRxMessage(hfdcan, FDCAN_RX_FIFO1, &rxHeader, rxData)
			== HAL_OK) {
		can->onMessageReceived(rxHeader, rxData);
	}
}

/* ---------------------------------------------------------------------------- */
uint32_t mapDLC(uint8_t dataLength) {
	switch (dataLength) {
	case 0:
		return FDCAN_DLC_BYTES_0;
	case 1:
		return FDCAN_DLC_BYTES_1;
	case 2:
		return FDCAN_DLC_BYTES_2;
	case 3:
		return FDCAN_DLC_BYTES_3;
	case 4:
		return FDCAN_DLC_BYTES_4;
	case 5:
		return FDCAN_DLC_BYTES_5;
	case 6:
		return FDCAN_DLC_BYTES_6;
	case 7:
		return FDCAN_DLC_BYTES_7;
	case 8:
		return FDCAN_DLC_BYTES_8;
	case 12:
		return FDCAN_DLC_BYTES_12;
	case 16:
		return FDCAN_DLC_BYTES_16;
	case 20:
		return FDCAN_DLC_BYTES_20;
	case 24:
		return FDCAN_DLC_BYTES_24;
	case 32:
		return FDCAN_DLC_BYTES_32;
	case 48:
		return FDCAN_DLC_BYTES_48;
	case 64:
		return FDCAN_DLC_BYTES_64;
	default:
		return 0xFFFFFFFF; // Invalid DLC value
	}
}


