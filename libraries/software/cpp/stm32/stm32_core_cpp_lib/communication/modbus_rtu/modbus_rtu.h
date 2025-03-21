/*
 * modbus_rtu.h
 *
 *  Created on: 29 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef COMMUNICATION_MODBUS_RTU_MODBUS_RTU_H_
#define COMMUNICATION_MODBUS_RTU_MODBUS_RTU_H_

/* TODO:
 * I want to support several hardware modes: UART_IT, UART_DMA. RS485 is something to enable, but Modbus over standard Serial should also be possible
 *
 *
 */

#include "../../core_includes.h"
#include "../../utils/core_utils.h"

#include <inttypes.h>
#include <stdbool.h>

#include "ModbusConfig.h"

#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "timers.h"
#include "semphr.h"

void resetAllModbusHandlers();


uint16_t calcCRC(uint8_t *Buffer, uint8_t u8length);
uint16_t word(uint8_t H, uint8_t L);

enum {
	EXC_FUNC_CODE = 1, EXC_ADDR_RANGE = 2, EXC_REGS_QUANT = 3, EXC_EXECUTE = 4
};

typedef enum {
	MB_UART_IT = 1, MB_UART_DMA = 2
} mb_hardware_t;

typedef enum MB_FC {
	MB_FC_READ_COILS = 1, /*!< FCT=1 -> read coils or digital outputs */
	MB_FC_READ_DISCRETE_INPUT = 2, /*!< FCT=2 -> read digital inputs */
	MB_FC_READ_REGISTERS = 3, /*!< FCT=3 -> read registers or analog outputs */
	MB_FC_READ_INPUT_REGISTER = 4, /*!< FCT=4 -> read analog inputs */
	MB_FC_WRITE_COIL = 5, /*!< FCT=5 -> write single coil or output */
	MB_FC_WRITE_REGISTER = 6, /*!< FCT=6 -> write single register */
	MB_FC_WRITE_MULTIPLE_COILS = 15, /*!< FCT=15 -> write multiple coils or outputs */
	MB_FC_WRITE_MULTIPLE_REGISTERS = 16 /*!< FCT=16 -> write multiple registers */
} mb_functioncode_t;

/**
 * @enum MESSAGE
 * @brief
 * Indexes to telegram frame positions
 */
typedef enum MESSAGE {
	ID = 0, //!< ID field
	FUNC, //!< Function code position
	ADD_HI, //!< Address high byte
	ADD_LO, //!< Address low byte
	NB_HI, //!< Number of coils or registers high byte
	NB_LO, //!< Number of coils or registers low byte
	BYTE_CNT  //!< byte counter
} mb_message_t;

typedef enum COM_STATES {
	COM_IDLE = 0, COM_WAITING = 1,

} mb_com_state_t;

typedef enum mb_error_t {
	ERR_NOT_MASTER = -1,
	ERR_POLLING = -2,
	ERR_BUFF_OVERFLOW = -3,
	ERR_BAD_CRC = -4,
	ERR_EXCEPTION = -5,
	ERR_BAD_SIZE = -6,
	ERR_BAD_ADDRESS = -7,
	ERR_TIME_OUT = -8,
	ERR_BAD_SLAVE_ID = -9,
	ERR_BAD_TCP_ID = -10,
	ERR_OK_QUERY = -11
} mb_error_t;

/**
 * @struct modbus_query_t
 * @brief
 * Master query structure:
 * This structure contains all the necessary fields to make the Master generate a Modbus query.
 * A Master may keep several of these structures and send them cyclically or
 * use them according to program needs.
 */
typedef struct {
	uint8_t u8id; /*!< Slave address between 1 and 247. 0 means broadcast */
	mb_functioncode_t u8fct; /*!< Function code: 1, 2, 3, 4, 5, 6, 15 or 16 */
	uint16_t u16RegAdd; /*!< Address of the first register to access at slave/s */
	uint16_t u16CoilsNo; /*!< Number of coils or registers to access */
	uint16_t *u16reg; /*!< Pointer to memory image in master */
	uint32_t *u32CurrentTask; /*!< Pointer to the task that will receive notifications from Modbus */
} modbus_query_t;

typedef struct modbus_config_t {
	UART_HandleTypeDef *huart;
	GPIO_TypeDef *EN_GPIOx;
	uint16_t EN_GPIO_Pin;
	mb_hardware_t hardware;
} modbus_config_t;

class ModbusMaster {
public:
	ModbusMaster();

	void init(modbus_config_t config);
	void start();

	void reset();

	void setTimeOut(uint16_t u16timeOut);
	uint16_t getTimeOut(); //!<get communication watch-dog timer value
	bool getTimeOutState(); //!<get communication watch-dog timer state

	void query(modbus_query_t telegram); // put a query in the queue tail
	void query(modbus_query_t telegram, uint32_t *threadId); // Query with a specific task to notify
	void queryInject(modbus_query_t telegram); //put a query in the queue head
	void queryInject(modbus_query_t telegram, uint32_t *threadId);

	int8_t lastError;
	uint8_t u8Buffer[MODBUS_BUFFER_SIZE];

	uint8_t u8BufferSize;
	uint8_t u8lastRec;
	uint16_t *u16regs;
	uint16_t u16InCnt, u16OutCnt, u16errCnt; //keep statistics of Modbus traffic
	uint16_t u16timeOut;
	uint16_t u16regsize;
	uint8_t dataRX;
	int8_t i8state;

	//Queue Modbus Telegram
//	QueueHandle_t QueueTelegramHandle;
//	osMessageQueueId_t QueueTelegramHandle;

	TaskHandle_t task_handle; // TODO: I might need the osThreadId_t and the TaskHandle_t
	osThreadId_t thread_handle;
	//Timer RX Modbus
	xTimerHandle xTimerT35;
	//Timer MasterTimeout
	xTimerHandle xTimerTimeout;
	//Semaphore for Modbus data
	osSemaphoreId_t ModBusSphrHandle;
	// RX ring buffer for USART
	core_utils_RingBuffer<128> xBufferRX;
	// type of hardware  TCP, USB CDC, USART


	int8_t sendQuery(modbus_query_t telegram);
	int16_t getRxBuffer();
	uint8_t validateRequest();
	uint8_t validateAnswer();

	void get_FC1();
	void get_FC3();

	int8_t process_FC1();
	int8_t process_FC3();
	int8_t process_FC5();
	int8_t process_FC6();
	int8_t process_FC15();
	int8_t process_FC16();

	modbus_config_t config;
private:

	void sendTxBuffer();

	void buildException(uint8_t u8exception);

};

void modbusMasterTask(void *argument);

#endif /* COMMUNICATION_MODBUS_RTU_MODBUS_RTU_H_ */
