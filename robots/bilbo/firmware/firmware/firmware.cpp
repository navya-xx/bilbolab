/*
 * firmware.cpp
 *
 *  Created on: Feb 13, 2023
 *      Author: lehmann_workstation
 *
 *  Description:
 *  Implementation of the TWIPR firmware control functions. This file defines
 *  the core logic for the firmware initialization, tasks, control mechanisms,
 *  and module integration for the TWIPR robot platform.
 */

#include "main.h"
#include "firmware_c.h"
#include "firmware.hpp"
#include <stdio.h>



/* Global Firmware Instance */
TWIPR_Firmware twipr_firmware;

/* Register Entries */
/* Firmware */

// Firmware State
core_utils_RegisterEntry<twipr_firmware_state_t, void> regentry_read_firmware_state(&register_map, REG_ADDRESS_R_FIRMWARE_STATE, &twipr_firmware.firmware_state);
// Firmware Tick
core_utils_RegisterEntry<uint32_t, void> regentry_read_firmware_tick(&register_map, REG_ADDRESS_R_FIRMWARE_TICK, &twipr_firmware.tick);
// Firmware Revison
core_utils_RegisterEntry<twipr_firmware_revision_t, void> regentry_read_firmware_revision(&register_map, REG_ADDRESS_R_FIRMWARE_REVISION, &twipr_firmware.revision);
// Debug Function
core_utils_RegisterEntry<uint8_t, uint8_t>regentry_f_firmware_debug(&register_map, REG_ADDRESS_F_FIRMWARE_DEBUGFUNCTION, &twipr_firmware, &TWIPR_Firmware::debug);
// Beep Function
core_utils_RegisterEntry<void, buzzer_beep_struct_t>regentry_f_firmware_beep(&register_map, REG_ADDRESS_F_FIRMWARE_BEEP, &rc_buzzer, &RobotControl_Buzzer::beep);
// Board Revision
core_utils_RegisterEntry<uint8_t, void>regentry_r_board_revision(&register_map, REG_ADDRESS_R_BOARD_REVISION, &board_revision);
// Max Wheel Speed Function
core_utils_RegisterEntry<float, float>regentry_rw_max_wheel_speed(&register_map, REG_ADDRESS_RW_MAX_WHEEL_SPEED, &twipr_firmware.supervisor.config.max_wheel_speed);
// External LED
core_utils_RegisterEntry<void, rgb_color_struct_t>regentry_function_setExternalLED(&register_map, REG_ADDRESS_F_EXTERNAL_LED, &extender, &RobotControl_Extender::rgbLEDStrip_extern_setColor);
// Debug 1 Flag
core_utils_RegisterEntry<uint8_t, uint8_t>regentry_debug1_rw(&register_map, REG_ADDRESS_RW_DEBUG_1, &twipr_firmware.debugData.debug1);

/* Control */
// Read Control Mode
core_utils_RegisterEntry<twipr_control_mode_t, void> regentry_read_control_mode(&register_map, REG_ADDRESS_R_CONTROL_MODE, &twipr_firmware.control.mode);
// Set Control Mode
core_utils_RegisterEntry<uint8_t, twipr_control_mode_t> regentry_function_control_setMode(&register_map, REG_ADDRESS_F_CONTROL_SET_MODE, &twipr_firmware.control, &TWIPR_ControlManager::setMode);
// Set Control K
core_utils_RegisterEntry<uint8_t, float[8]> regentry_function_control_setK(&register_map, REG_ADDRESS_F_CONTROL_SET_K, &twipr_firmware.control, &TWIPR_ControlManager::setBalancingGain);
// Set Direct Input
core_utils_RegisterEntry<void, twipr_control_direct_input_t> regentry_function_control_setDirectInput(&register_map, REG_ADDRESS_F_CONTROL_SET_DIRECT_INPUT, &twipr_firmware.control, &TWIPR_ControlManager::setDirectInput);
// Set Balancing Input
core_utils_RegisterEntry<void, twipr_balancing_control_input_t> regentry_function_control_setBalancingInput(&register_map, REG_ADDRESS_F_CONTROL_SET_BALANCING_INPUT, &twipr_firmware.control, &TWIPR_ControlManager::setBalancingInput);
// Set Speed Input
core_utils_RegisterEntry<void, twipr_speed_control_input_t> regentry_function_control_setSpeedInput(&register_map, REG_ADDRESS_F_CONTROL_SET_SPEED_INPUT, &twipr_firmware.control, &TWIPR_ControlManager::setSpeed);
// Set PID Forward
core_utils_RegisterEntry<uint8_t, float[3]> regentry_function_control_setPIDForward(&register_map, REG_ADDRESS_F_CONTROL_SET_FORWARD_PID, &twipr_firmware.control, &TWIPR_ControlManager::setVelocityControlForwardPID);
// Set PID Turn
core_utils_RegisterEntry<uint8_t, float[3]> regentry_function_control_setPIDTurn(&register_map, REG_ADDRESS_F_CONTROL_SET_TURN_PID, &twipr_firmware.control, &TWIPR_ControlManager::setVelocityControlTurnPID);
// Get Contol Configuration
core_utils_RegisterEntry<twipr_control_configuration_t, void> regentry_function_control_getControlConfiguration(&register_map, REG_ADDRESS_F_CONTROL_GET_CONFIGURATION, &twipr_firmware.control, &TWIPR_ControlManager::getControlConfiguration);

/* Sequencer */
core_utils_RegisterEntry<void, twipr_sequencer_sequence_data_t> regentry_function_sequencer_loadSequence(&register_map, REG_ADDRESS_F_SEQUENCE_LOAD, &twipr_firmware.sequencer, &TWIPR_Sequencer::loadSequence);
core_utils_RegisterEntry<void, uint16_t> regentry_function_sequencer_startSequence(&register_map,REG_ADDRESS_F_SEQUENCE_START ,&twipr_firmware.sequencer, &TWIPR_Sequencer::startSequence);
core_utils_RegisterEntry<void, void> regentry_function_sequencer_abortSequence(&register_map,REG_ADDRESS_F_SEQUENCE_STOP, &twipr_firmware.sequencer, &TWIPR_Sequencer::abortSequence);


/* Thread Attributes for Firmware and Control Tasks */
const osThreadAttr_t firmware_task_attributes = {
    .name = "firmware",
    .stack_size = 2560 * 4,
    .priority = (osPriority_t) osPriorityNormal,
};

const osThreadAttr_t control_task_attributes = {
    .name = "control",
    .stack_size = 2560 * 4,
    .priority = (osPriority_t) osPriorityNormal,
};

elapsedMillis activityTimer;


/**
 * @brief Initializes and starts the firmware task. This is the function called from the main function.
 */
void firmware() {
    osThreadNew(start_firmware_task, (void*)&twipr_firmware, &firmware_task_attributes);
}

/**
 * @brief Task wrapper to execute the firmware's main task function.
 * @param argument Pointer to the firmware object.
 */
void start_firmware_task(void* argument) {
    TWIPR_Firmware* firmware = (TWIPR_Firmware*)argument;
//    firmware->task = xTaskGetCurrentTaskHandle();
    firmware->helperTask();
}

/**
 * @brief Constructor for TWIPR_Firmware.
 */
TWIPR_Firmware::TWIPR_Firmware() {
    // Constructor logic can be extended if necessary
}

/**
 * @brief Main firmware task logic. This is initializing and starting the firmware. It then proceeds to do some monitoring.
 */
void TWIPR_Firmware::helperTask() {
    // Initialize and start the firmware components
    HAL_StatusTypeDef status;
    status = this->init();

    if (status){
    	while (true){
    		nop();
    	}
    }

    status = this->start();

    if (status){
    	while (true){
    		nop();
    	}
    }

    osDelay(150);
    // Signal successful initialization
    rc_buzzer.setConfig(900, 250, 1);
    rc_buzzer.start();

    // Initialize the LED state
    rc_rgb_led_side_1.setColor(0, 0, 0);
    rc_rgb_led_side_1.state(1);

    rgb_color_struct_t color_white_dim = {
    		.red = 2,
			.green = 2,
			.blue = 2
    };

    extender.rgbLEDStrip_extern_setColor(color_white_dim);


    elapsedMillis debug_timer;

    // Main task loop
    while (true) {

    	// Check the Control Mode LED Timer
    	if (this->timer_control_mode_led > 250){
    		this->timer_control_mode_led.reset();
    		this->setControlModeLed();
    	}

//    	// Debug
//    	if(debug_timer >= 1000){
//    		debug_timer.reset();
//    		this->comm.debugPrint("HALLO");
//    		this->comm.debugPrintf("Test Value: %d", x);
//    		x++;
//    	}
    }
}

/**
 * @brief Initializes all the firmware modules and configurations.
 */
HAL_StatusTypeDef TWIPR_Firmware::init() {
    // Initialize robot control and peripheral modules
    robot_control_init();
    robot_control_start();

    io_start();

    // Setup RGB LED and buzzer for feedback
    rc_rgb_led_status.setColor(120, 40, 0); // Orange
    rc_rgb_led_status.state(1);
    rc_buzzer.setConfig(800, 250, 1);
    rc_buzzer.start();

    osDelay(250); // Allow initialization delay

    // Communication module setup
    twipr_communication_config_t twipr_comm_config = {
        .huart = BOARD_CM4_UART,
        .hspi = BOARD_SPI_CM4,
        .notification_gpio_tx = core_utils_GPIO(CM4_SAMPLE_NOTIFICATION_PORT, CM4_SAMPLE_NOTIFICATION_PIN),
        .sequence_rx_buffer = this->sequencer.rx_buffer,
        .len_sequence_buffer = TWIPR_SEQUENCE_BUFFER_SIZE,
        .reset_uart_exti = CM4_UART_RESET_EXTI,
    };
    this->comm.init(twipr_comm_config);
    this->comm.start();

    // Sensors initialization
    twipr_sensors_config_t twipr_sensors_config = { .drive = &this->drive };
    this->sensors.init(twipr_sensors_config);

    // Estimation module setup
    twipr_estimation_config_t twipr_estimation_config = {
        .drive = &this->drive,
        .sensors = &this->sensors,
//        .enable_slip_detection = 1,
        .model = twipr_model_small,
    };
    this->estimation.init(twipr_estimation_config);

    // Control module initialization
    twipr_control_init_config_t twipr_control_config = {
        .estimation = &this->estimation,
        .drive = &this->drive,
        .max_torque = TWIPR_CONTROL_MAX_TORQUE,
        .freq = TWIPR_CONTROL_TASK_FREQ,
    };
    this->control.init(twipr_control_config);

    // Drive
    twipr_drive_can_config_t twipr_drive_config = {
    		.can = &this->comm.can,
			.id_left = 1,
			.id_right = 2,
			.direction_left = -1,
			.direction_right = 1,
			.torque_max = 0.4
    };

    HAL_StatusTypeDef status = this->drive.init(twipr_drive_config);

    if (status){
    	return status;
    }


    // Initialize safety module
    twipr_supervisor_config_t supervisor_config = {
    	.estimation = &this->estimation,
        .drive = &this->drive,
        .control = &this->control,
		.communication = &this->comm,
		.off_button = &off_button,
        .max_wheel_speed = TWIPR_SAFETY_MAX_WHEEL_SPEED,
    };
    this->supervisor.init(supervisor_config);

    // Sequencer setup
    twipr_sequencer_config_t sequencer_config = {
        .control = &this->control,
        .comm = &this->comm,
    };
    this->sequencer.init(sequencer_config);

    // Logging module configuration
    twipr_logging_config_t logging_config = {
        .firmware = this,
        .control = &this->control,
        .estimation = &this->estimation,
        .sensors = &this->sensors,
        .sequencer = &this->sequencer,
    };
    this->logging.init(logging_config);


    this->debugData = twipr_debug_sample_t{0};
    this->debugData.debug2 = 55;

    return HAL_OK;
}

/**
 * @brief Starts the various firmware components and control tasks.
 */
HAL_StatusTypeDef TWIPR_Firmware::start() {

    // Start the Sensors
    this->sensors.start();

    // Start the estimation module
    this->estimation.start();


    HAL_StatusTypeDef status = this->drive.start();

    if(status){
    	while(true){
    		nop();
    	}
    }

    // Start the control module
    this->control.start();

    // Start the safety module
    this->supervisor.start();

    // Start the Sequencer module
    this->sequencer.start();

    // Start the control task
    osThreadNew(start_firmware_control_task, (void*)&twipr_firmware, &control_task_attributes);

    // Set firmware state to RUNNING
    this->firmware_state = TWIPR_FIRMWARE_STATE_RUNNING;

    return HAL_OK;
}

/**
 * @brief Main control task function for the firmware.
 *
 * This task ensures periodic execution of control logic and manages the
 * state of the firmware. It checks timing constraints and handles error states.
 */
void TWIPR_Firmware::controlTask() {
    uint32_t global_tick;  // Current system tick
    uint32_t loop_time;    // Time taken for one control loop

    while (true) {
        global_tick = osKernelGetTickCount();  // Get current system tick

        // Execute the control task step
        this->controlTaskStep();

        // Measure the time taken for the loop
        loop_time = osKernelGetTickCount() - global_tick;

        // Check for race conditions or timing issues
        if (loop_time > (1000.0 / (float)TWIPR_CONTROL_TASK_FREQ)) {
            this->firmware_state = TWIPR_FIRMWARE_STATE_ERROR;
            this->error = TWIPR_ERROR_CRITICAL;
        }

        // Delay until the next loop execution
        osDelayUntil(global_tick + (uint32_t)(1000.0 / (float) TWIPR_CONTROL_TASK_FREQ));
    }
}

/**
 * @brief Performs a single step of the control logic.
 *
 * This method updates the state of the firmware based on its current mode,
 * manages the controller, updates the sequencer, and collects data samples
 * for logging.
 */
void TWIPR_Firmware::controlTaskStep() {


    switch (this->firmware_state) {
        case TWIPR_FIRMWARE_STATE_RUNNING: {

		if (activityTimer > 250) {
			activityTimer.reset();
			rc_activity_led.toggle();
		}

        	// Check all modules
        	//TODO

        	// Check for errors in the safety module
        	twipr_error_t error = this->supervisor.check();
        	if (!(error == TWIPR_ERROR_NONE)){
        		this->errorHandler(error);
        	}

            // Update the sequencer
            this->sequencer.update();

            // Update the controller
            this->control.update();

            // Collect samples for logging
            sample_buffer_state = this->logging.collectSamples();

            // If the logging buffer is full, provide data to the communication module
            if (sample_buffer_state == TWIPR_LOGGING_BUFFER_FULL) {
                this->comm.provideSampleData(this->logging.sample_buffer);
            }

            // Increment the tick counter
            this->tick++;

            // Set the status LED to green (normal operation)
            rc_rgb_led_status.setColor(0, 60, 0);
            break;
        }
        case TWIPR_FIRMWARE_STATE_ERROR: {
            // Set the status LED to red (error state)
            rc_rgb_led_status.setColor(120, 0, 0);
            break;
        }
        default: {
            // Handle undefined or unexpected states
            rc_rgb_led_status.setColor(120, 0, 0);
            break;
        }
    }
}


void TWIPR_Firmware::errorHandler(twipr_error_t error){
	switch (error) {
	case TWIPR_ERROR_CRITICAL:{
		this->control.stop();
		this->firmware_state = TWIPR_FIRMWARE_STATE_ERROR;
		break;
	}
	case TWIPR_ERROR_WARNING :{
		break;
	}
	case TWIPR_ERROR_NONE:{
		break;
	}
	}
}

/**
 * @brief Wrapper function to start the control task.
 * @param argument Pointer to the firmware object.
 */
void start_firmware_control_task(void* argument) {
    TWIPR_Firmware* firmware = (TWIPR_Firmware*)argument;
    firmware->controlTask();
}

/**
 * @brief Retrieves a logging sample with the current state and tick count.
 * @return A logging structure containing the current tick, state, and error code.
 */
twipr_logging_general_t TWIPR_Firmware::getSample() {
    twipr_logging_general_t sample = {
        .tick = this->tick,
        .state = this->firmware_state,
        .error = this->error,
    };
    return sample;
}

/**
 * @brief Updates the LED color based on the current control mode.
 *
 * This function changes the color of the side RGB LED to visually represent
 * the robot's current control mode:
 * - **Red**: TWIPR_CONTROL_MODE_OFF (The system is off)
 * - **Amber**: TWIPR_CONTROL_MODE_BALANCING (The system is in balancing mode)
 * - **Green**: TWIPR_CONTROL_MODE_VELOCITY (The system is in velocity mode)
 */
void TWIPR_Firmware::setControlModeLed() {
    // Check the current control mode and set the LED color accordingly
    if (this->control.mode == TWIPR_CONTROL_MODE_OFF) {
        rc_rgb_led_side_1.setColor(100, 0, 0); // Red for OFF mode
    } else if (this->control.mode == TWIPR_CONTROL_MODE_BALANCING) {
        rc_rgb_led_side_1.setColor(100, 70, 0); // Amber for Balancing
    } else if (this->control.mode == TWIPR_CONTROL_MODE_VELOCITY) {
        rc_rgb_led_side_1.setColor(0, 100, 0); // Green for Velocity
    }
}



/**
 * @brief Debug function used for custom debugging operations.
 * @param input The debug input value to process.
 */
uint8_t TWIPR_Firmware::debug(uint8_t input) {
    // Debugging logic can be implemented here
	return input + 1;
}
