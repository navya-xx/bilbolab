/*
 * bmi160_defs.h
 *
 *  Created on: 7 Jul 2022
 *      Author: Dustin Lehmann
 */

#ifndef CORE_SENSORS_IMU_BMI160_DEFS_H_
#define CORE_SENSORS_IMU_BMI160_DEFS_H_



/*
* TU Berlin - Project Automation - AviGA2.0
*
* IMU:
* The "Integrated Measurement Unit" BMX160 is used in this project, which is similar to Bosch's BMI160.
* The communication is using SPI and the driver from the BMI160 by Bosch in bmi160.c / bmi160.h.
* In imu.c, the initialization, setting,... for the IMU is performed.
*/

#ifndef INC_IMU_DEF_H_
#define INC_IMU_DEF_H_

/*---------------------FIFO-------------------- */
#define BMI160_FIFO_WATERMARK             			UINT16_C(900) 		//FIFO-Watermark: 88% / 900 Byte
#define BMI160_FIFO_INPUT             				UINT8_C(0xC0) 		//FIFO: ACC & GYR in FIFO (0b11000000)
#define BMI160_FIFO_DOWN							UINT8_C(0x88)		//FIFO: Filtered data input (0b10001000)

/*---------------------Register-Adress-------------------- */
//BMX160-Register-Map
#define BMI160_REG_COMMAND		             		UINT8_C(0x7E)
#define BMI160_REG_NV_CONF                   		UINT8_C(0x70)
#define BMI160_REG_ACCEL_CONFIG                 	UINT8_C(0x40)
#define BMI160_REG_ACCEL_RANGE                   	UINT8_C(0x41)
#define BMI160_REG_GYRO_CONFIG                   	UINT8_C(0x42)
#define BMI160_REG_GYRO_RANGE                    	UINT8_C(0x43)
#define BMI160_REG_FIFO_DOWN                     	UINT8_C(0x45)
#define BMI160_REG_FIFO_CONFIG_0                 	UINT8_C(0x46)
#define BMI160_REG_FIFO_CONFIG_1                 	UINT8_C(0x47)
#define BMI160_REG_INT_ENABLE_0                  	UINT8_C(0x50)
#define BMI160_REG_INT_ENABLE_1                  	UINT8_C(0x51)
#define BMI160_REG_INT_ENABLE_2                  	UINT8_C(0x52)
#define BMI160_REG_INT_OUT_CTRL                 	UINT8_C(0x53)
#define BMI160_REG_INT_MAP_0                     	UINT8_C(0x55)
#define BMI160_REG_INT_MAP_1                     	UINT8_C(0x56)
#define BMI160_REG_INT_MAP_2                     	UINT8_C(0x57)
#define BMI160_REG_FIFO_LENGTH_0                  	UINT8_C(0x22)
#define BMI160_REG_FIFO_LENGTH_1                   	UINT8_C(0x23)
#define BMI160_REG_FIFO_DATA                     	UINT8_C(0x24)

#define BMI160_REG_FOC		                     	UINT8_C(0x69)



#define BMI160_REG_GYR_X_LOW 						UINT8_C(0x0C)
#define BMI160_REG_GYR_X_HIGH 						UINT8_C(0x0D)
#define BMI160_REG_GYR_Y_LOW 						UINT8_C(0x0E)
#define BMI160_REG_GYR_Y_HIGH 						UINT8_C(0x0F)
#define BMI160_REG_GYR_Z_LOW 						UINT8_C(0x10)
#define BMI160_REG_GYR_Z_HIGH 						UINT8_C(0x11)

#define BMI160_REG_ACC_X_LOW 						UINT8_C(0x12)
#define BMI160_REG_ACC_X_HIGH 						UINT8_C(0x13)
#define BMI160_REG_ACC_Y_LOW 						UINT8_C(0x14)
#define BMI160_REG_ACC_Y_HIGH 						UINT8_C(0x15)
#define BMI160_REG_ACC_Z_LOW 						UINT8_C(0x16)
#define BMI160_REG_ACC_Z_HIGH 						UINT8_C(0x17)

#define BMI160_REG_SENSORTIME_0 					UINT8_C(0x18)
#define BMI160_REG_SENSORTIME_1 					UINT8_C(0x19)
#define BMI160_REG_SENSORTIME_2 					UINT8_C(0x1A)



/*---------------------Config-Masks-------------------- */
//BMX160-Register-Configure-Masks
#define BMI160_NULL                        			UINT8_C(0x0)
#define BMI160_ON                        			UINT8_C(0x1)
#define BMI160_OFF                        			UINT8_C(0x0)
#define BMI160_SPI_RD_MASK                        	UINT8_C(0x80)
#define BMI160_SPI_WR_MASK                        	UINT8_C(0x7F)

/*---------------------ACC-GYR-Config-------------------- */
/** Power mode settings */
/* Accel power mode */
#define BMI160_ACCEL_NORMAL_MODE                  UINT8_C(0x11)
#define BMI160_ACCEL_LOWPOWER_MODE                UINT8_C(0x12)
#define BMI160_ACCEL_SUSPEND_MODE                 UINT8_C(0x10)

/* Gyro power mode */
#define BMI160_GYRO_SUSPEND_MODE                  UINT8_C(0x14)
#define BMI160_GYRO_NORMAL_MODE                   UINT8_C(0x15)
#define BMI160_GYRO_FASTSTARTUP_MODE              UINT8_C(0x17)

/** Range settings */
/* Accel Range */
#define BMI160_ACCEL_RANGE_2G                     UINT8_C(0x03)
#define BMI160_ACCEL_RANGE_4G                     UINT8_C(0x05)
#define BMI160_ACCEL_RANGE_8G                     UINT8_C(0x08)
#define BMI160_ACCEL_RANGE_16G                    UINT8_C(0x0C)

/* Gyro Range */
#define BMI160_GYRO_RANGE_2000_DPS                UINT8_C(0x00)
#define BMI160_GYRO_RANGE_1000_DPS                UINT8_C(0x01)
#define BMI160_GYRO_RANGE_500_DPS                 UINT8_C(0x02)
#define BMI160_GYRO_RANGE_250_DPS                 UINT8_C(0x03)
#define BMI160_GYRO_RANGE_125_DPS                 UINT8_C(0x04)

/** Bandwidth settings */
/* Accel Bandwidth */
#define BMI160_ACCEL_BW_OSR4_AVG1                 UINT8_C(0x00 << 4)
#define BMI160_ACCEL_BW_OSR2_AVG2                 UINT8_C(0x01 << 4)
#define BMI160_ACCEL_BW_NORMAL_AVG4               UINT8_C(0x02 << 4)
#define BMI160_ACCEL_BW_RES_AVG8                  UINT8_C(0x03 << 4)
#define BMI160_ACCEL_BW_RES_AVG16                 UINT8_C(0x04 << 4)
#define BMI160_ACCEL_BW_RES_AVG32                 UINT8_C(0x05 << 4)
#define BMI160_ACCEL_BW_RES_AVG64                 UINT8_C(0x06 << 4)
#define BMI160_ACCEL_BW_RES_AVG128                UINT8_C(0x07 << 4)

/* Gyro Bandwidth */
#define BMI160_GYRO_BW_OSR4_MODE                  UINT8_C(0x00 << 4)
#define BMI160_GYRO_BW_OSR2_MODE                  UINT8_C(0x01 << 4)
#define BMI160_GYRO_BW_NORMAL_MODE                UINT8_C(0x02 << 4)

/* Output Data Rate settings */
/* Accel Output data rate */
#define BMI160_ACCEL_ODR_RESERVED                 UINT8_C(0x00)
#define BMI160_ACCEL_ODR_0_78HZ                   UINT8_C(0x01)
#define BMI160_ACCEL_ODR_1_56HZ                   UINT8_C(0x02)
#define BMI160_ACCEL_ODR_3_12HZ                   UINT8_C(0x03)
#define BMI160_ACCEL_ODR_6_25HZ                   UINT8_C(0x04)
#define BMI160_ACCEL_ODR_12_5HZ                   UINT8_C(0x05)
#define BMI160_ACCEL_ODR_25HZ                     UINT8_C(0x06)
#define BMI160_ACCEL_ODR_50HZ                     UINT8_C(0x07)
#define BMI160_ACCEL_ODR_100HZ                    UINT8_C(0x08)
#define BMI160_ACCEL_ODR_200HZ                    UINT8_C(0x09)
#define BMI160_ACCEL_ODR_400HZ                    UINT8_C(0x0A)
#define BMI160_ACCEL_ODR_800HZ                    UINT8_C(0x0B)
#define BMI160_ACCEL_ODR_1600HZ                   UINT8_C(0x0C)
#define BMI160_ACCEL_ODR_RESERVED0                UINT8_C(0x0D)
#define BMI160_ACCEL_ODR_RESERVED1                UINT8_C(0x0E)
#define BMI160_ACCEL_ODR_RESERVED2                UINT8_C(0x0F)

/* Gyro Output data rate */
#define BMI160_GYRO_ODR_RESERVED                  UINT8_C(0x00)
#define BMI160_GYRO_ODR_25HZ                      UINT8_C(0x06)
#define BMI160_GYRO_ODR_50HZ                      UINT8_C(0x07)
#define BMI160_GYRO_ODR_100HZ                     UINT8_C(0x08)
#define BMI160_GYRO_ODR_200HZ                     UINT8_C(0x09)
#define BMI160_GYRO_ODR_400HZ                     UINT8_C(0x0A)
#define BMI160_GYRO_ODR_800HZ                     UINT8_C(0x0B)
#define BMI160_GYRO_ODR_1600HZ                    UINT8_C(0x0C)
#define BMI160_GYRO_ODR_3200HZ                    UINT8_C(0x0D)





#define BMI160_CMD_FAST_OFFSET_CALIBRATION        UINT8_C(0x03)

#define BMI160_FOC_GYRO_ENABLE					  UINT8_C(0x40)
#define BMI160_FOC_GYRO_DISABLE					  UINT8_C(0x00)

/*---------------------FIFO-Config-------------------- */
#define BMI160_FIFO_FLUSH							UINT8_C(0xB0)	//FIFO: Flush the FIFO data

/*---------------------INT-Config-------------------- */
#define BMI160_INT_RST								UINT8_C(0xB1)	//INT: Resets interrupt engine

#endif /* INC_IMU_DEF_H_ */


#endif /* CORE_SENSORS_IMU_BMI160_DEFS_H_ */
