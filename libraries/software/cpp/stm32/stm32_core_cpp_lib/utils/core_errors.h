/*
 * errors.h
 *
 *  Created on: Jul 7, 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_UTILS_CORE_ERRORS_H_
#define CORE_UTILS_CORE_ERRORS_H_


#define CORE_ERROR_NOT_IMPLEMENTED 0x05
#define CORE_ERROR_HARDWARE_INIT 0x06
#define CORE_ERROR_WRONG_CONFIG 0x07


#define CORE_ERROR_HARDWARE_IMU 0x08

void core_ErrorHandler(int error_id);



#endif /* CORE_UTILS_CORE_ERRORS_H_ */
