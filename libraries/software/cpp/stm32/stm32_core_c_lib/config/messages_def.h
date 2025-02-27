/*
 * messages_def.h
 *
 *  Created on: 15 Apr 2022
 *      Author: Dustin Lehmann
 */

#ifndef CONFIG_MESSAGES_DEF_H_
#define CONFIG_MESSAGES_DEF_H_

/* General message definitions */

// Message structure
#define CORE_CONFIG_MSG_DATA_LENGTH_MAX 128
#define CORE_CONFIG_MSG_MIN_LEN 8
#define CORE_CONFIG_MSG_HEADER 0x55
#define CORE_CONFIG_MSG_FOOTER 0x5D

// Message layer
#define CORE_MSG_LAYER_CORE 0x01
#define CORE_MSG_LAYER_ROBOT 0x02
#define CORE_MSG_LAYER_APP 0x03

// Message type
#define CORE_MSG_TYPE_WRITE 0x01
#define CORE_MSG_TYPE_REQUEST 0x02
#define CORE_MSG_TYPE_ANSWER 0x03
#define CORE_MSG_TYPE_STREAM 0x04
#define CORE_MSG_TYPE_ERROR 0x05

/* Core messages */



#endif /* CONFIG_MESSAGES_DEF_H_ */
