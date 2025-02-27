/*
 * modbus_rtu.cpp
 *
 *  Created on: 29 Jul 2022
 *      Author: Dustin Lehmann
 */

#include "modbus_rtu.h"
#include "core_hardware_UART.h"

#define MAX_MODBUS_HANDLERS 2

ModbusMaster *handlers[MAX_MODBUS_HANDLERS];
uint8_t num_handlers = 0;

const osThreadAttr_t task_attributes = { .name = "TaskModbusMaster",
		.stack_size = 1028 * 4, .priority = (osPriority_t) osPriorityNormal };

const osSemaphoreAttr_t semaphore_attributes = { .name = "ModBusSphr" };

osMessageQueueId_t modbus_query_queue;

const unsigned char fctsupported[] = { MB_FC_READ_COILS,
		MB_FC_READ_DISCRETE_INPUT, MB_FC_READ_REGISTERS,
		MB_FC_READ_INPUT_REGISTER, MB_FC_WRITE_COIL, MB_FC_WRITE_REGISTER,
		MB_FC_WRITE_MULTIPLE_COILS, MB_FC_WRITE_MULTIPLE_REGISTERS };

static void vTimerCallbackT35(TimerHandle_t *pxTimer);
static void vTimerCallbackTimeout(TimerHandle_t *pxTimer);

void uartRxCompleteDMA_callback(UART_HandleTypeDef *huart, uint16_t size);
static void uartRxCompleteIT_callback(UART_HandleTypeDef *huart);
void uartTxCompleteDMA_callback(UART_HandleTypeDef *huart);

/* ================================================================ */
ModbusMaster::ModbusMaster() {

}
/* ================================================================ */
void ModbusMaster::init(modbus_config_t config) {

	this->config = config;

	if (num_handlers < MAX_MODBUS_HANDLERS) {

		// Initialize the ring buffer
		this->xBufferRX.clear();

		// Create the master task and the queue for telegrams
		this->thread_handle = osThreadNew(modbusMasterTask, this,
				&task_attributes);

		//
		this->u16timeOut = 20;
		// Initialize the timeout timer
		this->xTimerTimeout = xTimerCreate("xTimerTimeout", // Just a text name, not used by the kernel.
				this->u16timeOut,     		// The timer period in ticks.
				pdFALSE, // The timers will auto-reload themselves when they expire.
				(void*) this->xTimerTimeout, // Assign each timer a unique id equal to its array index.
				(TimerCallbackFunction_t) vTimerCallbackTimeout // Each timer calls the same callback when it expires.
				);

		if (this->xTimerTimeout == NULL) {
			while (1)
				; // TODO error creating timer, check heap and stack size
		}

		modbus_query_queue = osMessageQueueNew(MAX_TELEGRAMS,
				sizeof(modbus_query_t), NULL);

		if (modbus_query_queue == NULL) {
			while (1)
				; //error creating queue for telegrams, check heap and stack size
		}

		if (this->thread_handle == NULL) {
			while (1)
				; //Error creating Modbus task, check heap and stack size
		}

		this->xTimerT35 = xTimerCreate("TimerT35", // Just a text name, not used by the kernel.
				T35,     // The timer period in ticks.
				pdFALSE, // The timers will auto-reload themselves when they expire.
				(void*) this->xTimerT35, // Assign each timer a unique id equal to its array index.
				(TimerCallbackFunction_t) vTimerCallbackT35 // Each timer calls the same callback when it expires.
				);
		if (this->xTimerT35 == NULL) {
			while (1)
				; //Error creating the timer, check heap and stack size
		}
		this->ModBusSphrHandle = osSemaphoreNew(1, 1, &semaphore_attributes);

		if (this->ModBusSphrHandle == NULL) {
			while (1)
				; //Error creating the semaphore, check heap and stack size
		}

		handlers[num_handlers] = this;
		num_handlers++;
	} else {
		while (1)
			; //error no more Modbus handlers supported
	}

	// Initialize the UART

	// TODO: Add UART Initialization and checking whether it is correctly initialized
	// Should I be able to use one of my UART classes?

}
/* ================================================================ */
void ModbusMaster::start() {

	HAL_UART_Abort(this->config.huart);

	if (this->config.EN_GPIOx != NULL) {
		// Set RS485 Transmitter to transmit mode
		HAL_GPIO_WritePin(config.EN_GPIOx, config.EN_GPIO_Pin, GPIO_PIN_RESET);
	}

	// Wait until UART is ready
	while (HAL_UART_GetState(this->config.huart) != HAL_UART_STATE_READY) {

	}

	if (this->config.hardware == MB_UART_IT) {

		// Register the callback for the UART Interrupt
		HAL_UART_RegisterCallback(this->config.huart,
				HAL_UART_RX_COMPLETE_CB_ID, uartRxCompleteIT_callback);

//		HAL_UART_RegisterCallback(this->huart, HAL_UART_TX_COMPLETE_CB_ID, uartTxCompleteIT_callback);

		// Receive data from serial port for Modbus using interrupt
		if (HAL_UART_Receive_IT(this->config.huart, &this->dataRX, 1)
				!= HAL_OK) {
			while (1) {
				//error in your initialization code
			}
		}
	} else if (this->config.hardware == MB_UART_DMA) {
		HAL_UART_RegisterRxEventCallback(this->config.huart,
				uartRxCompleteDMA_callback);

		HAL_UART_RegisterCallback(this->config.huart,
				HAL_UART_TX_COMPLETE_CB_ID, uartTxCompleteDMA_callback);

		if (HAL_UARTEx_ReceiveToIdle_DMA(this->config.huart,
				this->xBufferRX.buffer,
				MAX_BUFFER) != HAL_OK) {
			while (1) {
				//error in your initialization code
			}
		}
		__HAL_DMA_DISABLE_IT(this->config.huart->hdmarx, DMA_IT_HT);
	}

	// Reset all statistics
	this->u8lastRec = 0;
	this->u8BufferSize = 0;
	this->u16InCnt = 0;
	this->u16OutCnt = 0;
	this->u16errCnt = 0;
}

void ModbusMaster::reset() {
 // Delete the master Task
	num_handlers --;
	vTaskDelete(this->task_handle);
	this->init(this->config);
	this->start();
}

/* ================================================================ */
void modbusMasterTask(void *argument) {
	ModbusMaster *master = (ModbusMaster*) argument;

	// Get the task handle for later notifying this task
	master->task_handle = xTaskGetCurrentTaskHandle();

	uint32_t ulNotificationValue;
	modbus_query_t telegram;

	for (;;) {
		/*Wait indefinitely for a telegram to send */
		osMessageQueueGet(modbus_query_queue, &telegram, 0, portMAX_DELAY);

		// This is the case for implementations with only USART support
		master->sendQuery(telegram);
		/* Block indefinitely until a Modbus Frame arrives or query timeouts*/
		ulNotificationValue = ulTaskNotifyTake(pdTRUE, 200);

		// notify the task the request timeout
		master->lastError = 0;
		if (ulNotificationValue) {
			master->i8state = COM_IDLE;
			master->lastError = ERR_TIME_OUT;
			master->u16errCnt++;
			xTaskNotify((TaskHandle_t )telegram.u32CurrentTask,
					master->lastError, eSetValueWithOverwrite);
			continue;
		}
		master->getRxBuffer();

		if (master->u8BufferSize < 6) {

			master->i8state = COM_IDLE;
			master->lastError = ERR_BAD_SIZE;
			master->u16errCnt++;
			xTaskNotify((TaskHandle_t )telegram.u32CurrentTask,
					master->lastError, eSetValueWithOverwrite);
			continue;
		}

		xTimerStop(master->xTimerTimeout, 0); // cancel timeout timer

		// validate message: id, CRC, FCT, exception
		int8_t u8exception = master->validateAnswer();
		if (u8exception != 0) {
			master->i8state = COM_IDLE;
			master->lastError = u8exception;
			xTaskNotify((TaskHandle_t )telegram.u32CurrentTask,
					master->lastError, eSetValueWithOverwrite);
			continue;
		}

		master->lastError = u8exception; // Should be 0

		osSemaphoreAcquire(master->ModBusSphrHandle, portMAX_DELAY); //before processing the message get the semaphore
		// process answer
		switch (master->u8Buffer[FUNC]) {
		case MB_FC_READ_COILS:
		case MB_FC_READ_DISCRETE_INPUT:
			//call get_FC1 to transfer the incoming message to u16regs buffer
			master->get_FC1();
			break;
		case MB_FC_READ_INPUT_REGISTER:
		case MB_FC_READ_REGISTERS:
			// call get_FC3 to transfer the incoming message to u16regs buffer
			master->get_FC3();
			break;
		case MB_FC_WRITE_COIL:
		case MB_FC_WRITE_REGISTER:
		case MB_FC_WRITE_MULTIPLE_COILS:
		case MB_FC_WRITE_MULTIPLE_REGISTERS:
			// nothing to do
			break;
		default:
			break;
		}
		master->i8state = COM_IDLE;

		if (master->lastError == 0) // no error the error_OK, we need to use a different value than 0 to detect the timeout
				{
			osSemaphoreRelease(master->ModBusSphrHandle);
			xTaskNotify((TaskHandle_t )telegram.u32CurrentTask, ERR_OK_QUERY,
					eSetValueWithOverwrite);
		}
		continue;
	}
}

/* ================================================================ */
void ModbusMaster::query(modbus_query_t telegram) {
	// Add the telegram to the TX tail of the telegram queue
	telegram.u32CurrentTask = (uint32_t*) osThreadGetId();
	osMessageQueuePut(modbus_query_queue, &telegram, 0, 0);
}

/* ================================================================ */
void ModbusMaster::query(modbus_query_t telegram, uint32_t *threadId) {
	// Add the telegram to the TX tail of the telegram queue
	telegram.u32CurrentTask = threadId;
//	xQueueSendToBack(this->QueueTelegramHandle, &telegram, 0);
	osMessageQueuePut(modbus_query_queue, &telegram, 0, 0);
}
/* ================================================================ */
void ModbusMaster::queryInject(modbus_query_t telegram) {
	telegram.u32CurrentTask = (uint32_t*) osThreadGetId();
	osMessageQueuePut(modbus_query_queue, &telegram, 0, 0);
}

/* ================================================================ */
void ModbusMaster::queryInject(modbus_query_t telegram, uint32_t *threadId) {
	telegram.u32CurrentTask = threadId;
	osMessageQueuePut(modbus_query_queue, &telegram, 0, 0);
}

/* ================================================================ */
void ModbusMaster::get_FC1() {
	uint8_t u8byte, i;
	u8byte = 3;
	for (i = 0; i < this->u8Buffer[2]; i++) {

		if (i % 2) {
			this->u16regs[i / 2] = word(this->u8Buffer[i + u8byte],
					lowByte(this->u16regs[i / 2]));
		} else {

			this->u16regs[i / 2] = word(highByte(this->u16regs[i / 2]),
					this->u8Buffer[i + u8byte]);
		}

	}
}

/* ================================================================ */
void ModbusMaster::get_FC3() {
	/**
	 * This method processes functions 3 & 4 (for master)
	 * This method puts the slave answer into master data buffer
	 *
	 * @ingroup register
	 */

	uint8_t u8byte, i;
	u8byte = 3;

	for (i = 0; i < this->u8Buffer[2] / 2; i++) {
		this->u16regs[i] = word(this->u8Buffer[u8byte],
				this->u8Buffer[u8byte + 1]);
		u8byte += 2;
//		this->u16regs[i] = this->u8Buffer[u8byte];
//		u8byte += 1;
	}

}

/* ================================================================ */
/**
 * @brief
 * This method validates slave incoming messages
 *
 * @return 0 if OK, EXCEPTION if anything fails
 * @ingroup this Modbus handler
 */
uint8_t ModbusMaster::validateRequest() {
	uint16_t u16MsgCRC;
	u16MsgCRC = ((this->u8Buffer[this->u8BufferSize - 2] << 8)
			| this->u8Buffer[this->u8BufferSize - 1]); // combine the crc Low & High bytes

	if (calcCRC(this->u8Buffer, this->u8BufferSize - 2) != u16MsgCRC) {
		this->u16errCnt++;
		return ERR_BAD_CRC;
	}

	// check fct code
	bool isSupported = false;
	for (uint8_t i = 0; i < sizeof(fctsupported); i++) {
		if (fctsupported[i] == this->u8Buffer[FUNC]) {
			isSupported = 1;
			break;
		}
	}
	if (!isSupported) {
		this->u16errCnt++;
		return EXC_FUNC_CODE;
	}

	// check start address & nb range
	uint16_t u16AdRegs = 0;
	uint16_t u16NRegs = 0;

	//uint8_t u8regs;
	switch (this->u8Buffer[FUNC]) {
	case MB_FC_READ_COILS:
	case MB_FC_READ_DISCRETE_INPUT:
	case MB_FC_WRITE_MULTIPLE_COILS:
		u16AdRegs = word(this->u8Buffer[ADD_HI], this->u8Buffer[ADD_LO]) / 16;
		u16NRegs = word(this->u8Buffer[NB_HI], this->u8Buffer[NB_LO]) / 16;
		if (word(this->u8Buffer[NB_HI], this->u8Buffer[NB_LO]) % 16)
			u16NRegs++; // check for incomplete words
		// verify address range
		if ((u16AdRegs + u16NRegs) > this->u16regsize)
			return EXC_ADDR_RANGE;

		//verify answer frame size in bytes

		u16NRegs = word(this->u8Buffer[NB_HI], this->u8Buffer[NB_LO]) / 8;
		if (word(this->u8Buffer[NB_HI], this->u8Buffer[NB_LO]) % 8)
			u16NRegs++;
		u16NRegs = u16NRegs + 5; // adding the header  and CRC ( Slave address + Function code  + number of data bytes to follow + 2-byte CRC )
		if (u16NRegs > 256)
			return EXC_REGS_QUANT;

		break;
	case MB_FC_WRITE_COIL:
		u16AdRegs = word(this->u8Buffer[ADD_HI], this->u8Buffer[ADD_LO]) / 16;
		if (word(this->u8Buffer[ADD_HI], this->u8Buffer[ADD_LO]) % 16)
			u16AdRegs++;	// check for incomplete words
		if (u16AdRegs > this->u16regsize)
			return EXC_ADDR_RANGE;
		break;
	case MB_FC_WRITE_REGISTER:
		u16AdRegs = word(this->u8Buffer[ADD_HI], this->u8Buffer[ADD_LO]);
		if (u16AdRegs > this->u16regsize)
			return EXC_ADDR_RANGE;
		break;
	case MB_FC_READ_REGISTERS:
	case MB_FC_READ_INPUT_REGISTER:
	case MB_FC_WRITE_MULTIPLE_REGISTERS:
		u16AdRegs = word(this->u8Buffer[ADD_HI], this->u8Buffer[ADD_LO]);
		u16NRegs = word(this->u8Buffer[NB_HI], this->u8Buffer[NB_LO]);
		if ((u16AdRegs + u16NRegs) > this->u16regsize)
			return EXC_ADDR_RANGE;

		//verify answer frame size in bytes
		u16NRegs = u16NRegs * 2 + 5; // adding the header  and CRC
		if (u16NRegs > 256)
			return EXC_REGS_QUANT;
		break;
	}
	return 0; // OK, no exception code thrown
}

/* ================================================================ */
/**
 * @brief
 * This method validates master incoming messages
 *
 * @return 0 if OK, EXCEPTION if anything fails
 * @ingroup buffer
 */
uint8_t ModbusMaster::validateAnswer() {
	// check message crc vs calculated crc

	uint16_t u16MsgCRC = ((this->u8Buffer[this->u8BufferSize - 2] << 8)
			| this->u8Buffer[this->u8BufferSize - 1]); // combine the crc Low & High bytes
	if (calcCRC(this->u8Buffer, this->u8BufferSize - 2) != u16MsgCRC) {
		this->u16errCnt++;
		return ERR_BAD_CRC;
	}

	// check exception
	if ((this->u8Buffer[FUNC] & 0x80) != 0) {
		this->u16errCnt++;
		return ERR_EXCEPTION;
	}

	// check fct code
	bool isSupported = false;
	for (uint8_t i = 0; i < sizeof(fctsupported); i++) {
		if (fctsupported[i] == this->u8Buffer[FUNC]) {
			isSupported = 1;
			break;
		}
	}
	if (!isSupported) {
		this->u16errCnt++;
		return EXC_FUNC_CODE;
	}

	return 0; // OK, no exception code thrown
}

/* ================================================================ */
int16_t ModbusMaster::getRxBuffer() {

	int16_t i16result;

	if (this->config.hardware == MB_UART_IT) {
		HAL_UART_AbortReceive_IT(this->config.huart); // disable interrupts to avoid race conditions on serial port
	}

	if (this->xBufferRX.overflow) {
		this->xBufferRX.clear();
		i16result = ERR_BUFF_OVERFLOW;
	} else {
		this->u8BufferSize = this->xBufferRX.get_all_bytes(this->u8Buffer);
		this->u16InCnt++;
		i16result = this->u8BufferSize;
	}

	if (this->config.hardware == MB_UART_IT) {
		HAL_UART_Receive_IT(this->config.huart, &this->dataRX, 1);
	}

	return i16result;
}

/* ================================================================ */
void uartRxCompleteIT_callback(UART_HandleTypeDef *huart) {
	nop();
}

/* ================================================================ */
void uartRxCompleteDMA_callback(UART_HandleTypeDef *huart, uint16_t size) {
	BaseType_t xHigherPriorityTaskWoken = pdFALSE;

	int i;
	for (i = 0; i < num_handlers; i++) {
		if (handlers[i]->config.huart == huart) {

			if (handlers[i]->config.hardware == MB_UART_DMA) {
				if (size) //check if we have received any byte
				{
					handlers[i]->xBufferRX.available = size;
					handlers[i]->xBufferRX.overflow = false;

					while (HAL_UARTEx_ReceiveToIdle_DMA(
							handlers[i]->config.huart,
							handlers[i]->xBufferRX.buffer, MAX_BUFFER) != HAL_OK) {
						HAL_UART_DMAStop(handlers[i]->config.huart);

					}
					__HAL_DMA_DISABLE_IT(handlers[i]->config.huart->hdmarx,
							DMA_IT_HT); // we don't need half-transfer interrupt

					xTaskNotifyFromISR(handlers[i]->task_handle, 0,
							eSetValueWithOverwrite, &xHigherPriorityTaskWoken);
				}
			}
			break;
		}
	}
	portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

/* ================================================================ */
void uartTxCompleteDMA_callback(UART_HandleTypeDef *huart) {
	BaseType_t xHigherPriorityTaskWoken = pdFALSE;
	int i;
	for (i = 0; i < num_handlers; i++) {
		if (handlers[i]->config.huart == huart) {
			// notify the end of TX
//			vTaskNotifyGiveFromISR(handlers[i]->task_handle, &xHigherPriorityTaskWoken);
			xTaskNotifyFromISR(handlers[i]->task_handle, 0, eNoAction,
					&xHigherPriorityTaskWoken);
			break;
		}

	}
	portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

/* ================================================================ */
void vTimerCallbackT35(TimerHandle_t *pxTimer) {
	//Notify that a stream has just arrived
	int i;
	//TimerHandle_t aux;
	for (i = 0; i < num_handlers; i++) {

		if ((TimerHandle_t*) handlers[i]->xTimerT35 == pxTimer) {
			xTimerStop(handlers[i]->xTimerTimeout, 0);
			xTaskNotify(handlers[i]->task_handle, 0, eSetValueWithOverwrite); // TODO this conversion to TaskHandle_t might not work and I have to save the real TaskHandle_t
		}

	}
}

/* ================================================================ */
void vTimerCallbackTimeout(TimerHandle_t *pxTimer) {
	//Notify that a stream has just arrived
	int i;
	//TimerHandle_t aux;
	for (i = 0; i < num_handlers; i++) {

		if ((TimerHandle_t*) handlers[i]->xTimerTimeout == pxTimer) {
			xTaskNotify((TaskHandle_t ) handlers[i]->task_handle, ERR_TIME_OUT,
					eSetValueWithOverwrite); // TODO this conversion to TaskHandle_t might not work and I have to save the real TaskHandle_t
		}

	}

}

/* ================================================================ */
int8_t ModbusMaster::sendQuery(modbus_query_t telegram) {
	uint8_t u8regsno, u8bytesno;
	int8_t error = 0;
	osSemaphoreAcquire(this->ModBusSphrHandle, portMAX_DELAY);

	if (this->i8state != COM_IDLE)
		error = ERR_POLLING;
	if ((telegram.u8id == 0) || (telegram.u8id > 247))
		error = ERR_BAD_SLAVE_ID;

	if (error) {
		this->lastError = error;
		osSemaphoreRelease(this->ModBusSphrHandle);
		return error;
	}

	this->u16regs = telegram.u16reg;

	// telegram header
	this->u8Buffer[ID] = telegram.u8id;
	this->u8Buffer[FUNC] = telegram.u8fct;
	this->u8Buffer[ADD_HI] = highByte(telegram.u16RegAdd);
	this->u8Buffer[ADD_LO] = lowByte(telegram.u16RegAdd);
//
	switch (telegram.u8fct) {
	case MB_FC_READ_COILS:
	case MB_FC_READ_DISCRETE_INPUT:
	case MB_FC_READ_REGISTERS:
	case MB_FC_READ_INPUT_REGISTER:
		this->u8Buffer[NB_HI] = highByte(telegram.u16CoilsNo);
		this->u8Buffer[NB_LO] = lowByte(telegram.u16CoilsNo);
		this->u8BufferSize = 6;
		break;
	case MB_FC_WRITE_COIL:
		this->u8Buffer[NB_HI] = ((telegram.u16reg[0] > 0) ? 0xff : 0);
		this->u8Buffer[NB_LO] = 0;
		this->u8BufferSize = 6;
		break;
	case MB_FC_WRITE_REGISTER:
		this->u8Buffer[NB_HI] = highByte(telegram.u16reg[0]);
		this->u8Buffer[NB_LO] = lowByte(telegram.u16reg[0]);
		this->u8BufferSize = 6;
		break;
	case MB_FC_WRITE_MULTIPLE_COILS: // TODO: implement "sending coils"
		u8regsno = telegram.u16CoilsNo / 16;
		u8bytesno = u8regsno * 2;
		if ((telegram.u16CoilsNo % 16) != 0) {
			u8bytesno++;
			u8regsno++;
		}

		this->u8Buffer[NB_HI] = highByte(telegram.u16CoilsNo);
		this->u8Buffer[NB_LO] = lowByte(telegram.u16CoilsNo);
		this->u8Buffer[BYTE_CNT] = u8bytesno;
		this->u8BufferSize = 7;

		for (uint16_t i = 0; i < u8bytesno; i++) {
			if (i % 2) {
				this->u8Buffer[this->u8BufferSize] = lowByte(
						telegram.u16reg[i / 2]);
			} else {
				this->u8Buffer[this->u8BufferSize] = highByte(
						telegram.u16reg[i / 2]);

			}
			this->u8BufferSize++;
		}
		break;

	case MB_FC_WRITE_MULTIPLE_REGISTERS:
		this->u8Buffer[NB_HI] = highByte(telegram.u16CoilsNo);
		this->u8Buffer[NB_LO] = lowByte(telegram.u16CoilsNo);
		this->u8Buffer[BYTE_CNT] = (uint8_t) (telegram.u16CoilsNo * 2);
		this->u8BufferSize = 7;

		for (uint16_t i = 0; i < telegram.u16CoilsNo; i++) {

			this->u8Buffer[this->u8BufferSize] = highByte(telegram.u16reg[i]);
			this->u8BufferSize++;
			this->u8Buffer[this->u8BufferSize] = lowByte(telegram.u16reg[i]);
			this->u8BufferSize++;
		}
		break;
	}

	this->sendTxBuffer();

	osSemaphoreRelease(this->ModBusSphrHandle);
	this->i8state = COM_WAITING;
	this->lastError = 0;
	return 0;
}

/* ================================================================ */
void ModbusMaster::sendTxBuffer() {
	uint16_t u16crc = calcCRC(this->u8Buffer, this->u8BufferSize);
	this->u8Buffer[this->u8BufferSize] = u16crc >> 8;
	this->u8BufferSize++;
	this->u8Buffer[this->u8BufferSize] = u16crc & 0x00ff;
	this->u8BufferSize++;

	if (this->config.EN_GPIOx != NULL) {
		//enable transmitter, disable receiver to avoid echo on RS485 transceivers
		HAL_HalfDuplex_EnableTransmitter(this->config.huart);
		HAL_GPIO_WritePin(this->config.EN_GPIOx, this->config.EN_GPIO_Pin,
				GPIO_PIN_SET);
	}

	if (this->config.hardware == MB_UART_IT) {
		HAL_UART_Transmit_IT(this->config.huart, this->u8Buffer,
				this->u8BufferSize);
	} else if (this->config.hardware == MB_UART_DMA) {
		HAL_UART_Transmit_DMA(this->config.huart, this->u8Buffer,
				this->u8BufferSize);
	}

	ulTaskNotifyTake(pdTRUE, 20); //wait notification from TXE interrupt
	/*
	 * If you are porting the library to a different MCU check the
	 * USART datasheet and add the corresponding family in the following
	 * preprocessor conditions
	 */
#if defined(STM32H7)  || defined(STM32F3) || defined(STM32L4)
	while ((this->config.huart->Instance->ISR & USART_ISR_TC) == 0) {

	}
#else
	  // F429, F103, L152 ...
  while((this->config.huart->Instance->SR & USART_SR_TC) ==0 ) {

  }
#endif

	if (this->config.EN_GPIOx != NULL) {

		//return RS485 transceiver to receive mode
		HAL_GPIO_WritePin(this->config.EN_GPIOx, this->config.EN_GPIO_Pin,
				GPIO_PIN_RESET);
		//enable receiver, disable transmitter
		HAL_HalfDuplex_EnableReceiver(this->config.huart);

	}

	// set timeout for master query

	xTimerReset(this->xTimerTimeout, 0);

	this->u8BufferSize = 0;
	// increase message counter
	this->u16OutCnt++;
}

/**
 * @brief
 * This method creates a word from 2 bytes
 *
 * @return uint16_t (word)
 * @ingroup H  Most significant byte
 * @ingroup L  Less significant byte
 */
uint16_t word(uint8_t H, uint8_t L) {
	bytesFields W;
	W.u8[0] = L;
	W.u8[1] = H;

	return W.u16[0];
}

/**
 * @brief
 * This method calculates CRC
 *
 * @return uint16_t calculated CRC value for the message
 * @ingroup Buffer
 * @ingroup u8length
 */
uint16_t calcCRC(uint8_t *Buffer, uint8_t u8length) {
	unsigned int temp, temp2, flag;
	temp = 0xFFFF;
	for (unsigned char i = 0; i < u8length; i++) {
		temp = temp ^ Buffer[i];
		for (unsigned char j = 1; j <= 8; j++) {
			flag = temp & 0x0001;
			temp >>= 1;
			if (flag)
				temp ^= 0xA001;
		}
	}
	// Reverse byte order.
	temp2 = temp >> 8;
	temp = (temp << 8) | temp2;
	temp &= 0xFFFF;
	// the returned value is already swapped
	// crcLo byte is first & crcHi byte is last
	return temp;

}
