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

/* Firmware Test Register Entry */
uint8_t test() {
    return 2;
}
core_utils_RegisterEntry<uint8_t, void> reg_test(&register_map, 0xCC, &test);

/* Firmware State Register Entry */
core_utils_RegisterEntry<twipr_firmware_state_t, void> reg_fw_state(&register_map, REG_ADDRESS_R_FIRMWARE_STATE, &twipr_firmware.firmware_state);

/* Firmware Tick Register Entry */
core_utils_RegisterEntry<uint32_t, void> reg_fw_tick(&register_map, REG_ADDRESS_R_FIRMWARE_TICK, &twipr_firmware.tick);

/* Firmware Revision Register Entry */
core_utils_RegisterEntry<twipr_firmware_revision_t, void> reg_fw_rev(&register_map, REG_ADDRESS_R_FIRMWARE_REVISION, &twipr_firmware.revision);

/* Firmware Debug Function Register Entry */
core_utils_RegisterEntry<uint8_t, uint8_t> reg_fw_debug(&register_map, REG_ADDRESS_F_FIRMWARE_DEBUGFUNCTION, &twipr_firmware, &TWIPR_Firmware::debug);

/* Firmware Beep Function Register Entry */
core_utils_RegisterEntry<void, buzzer_beep_struct_t> reg_fw_beep(&register_map, REG_ADDRESS_F_FIRMWARE_BEEP, &rc_buzzer, &RobotControl_Buzzer::beep);

/* Board Revision Register Entry */
core_utils_RegisterEntry<uint8_t, void> reg_board_rev(&register_map, REG_ADDRESS_R_BOARD_REVISION, &board_revision);

/* Max Wheel Speed Register Entry */
core_utils_RegisterEntry<float, float> reg_max_speed(&register_map, REG_ADDRESS_RW_MAX_WHEEL_SPEED, &twipr_firmware.supervisor.config.max_wheel_speed);

/* External LED Function Register Entry */
core_utils_RegisterEntry<void, rgb_color_struct_t> reg_set_ext_led(&register_map, REG_ADDRESS_F_EXTERNAL_LED, &extender, &RobotControl_Extender::rgbLEDStrip_extern_setColor);

/* Debug 1 Flag Register Entry */
core_utils_RegisterEntry<uint8_t, uint8_t> reg_debug1(&register_map, REG_ADDRESS_RW_DEBUG_1, &twipr_firmware.debugData.debug1);

/* Control */

/* Read Control Mode Register Entry */
core_utils_RegisterEntry<twipr_control_mode_t, void> reg_ctrl_mode(&register_map, REG_ADDRESS_R_CONTROL_MODE, &twipr_firmware.control.mode);

/* Set Control Mode Function Register Entry */
core_utils_RegisterEntry<uint8_t, twipr_control_mode_t> reg_set_mode(&register_map, REG_ADDRESS_F_CONTROL_SET_MODE, &twipr_firmware.control, &TWIPR_ControlManager::setMode);

/* Set Control Gain Function Register Entry */
core_utils_RegisterEntry<uint8_t, float[8]> reg_set_gain(&register_map, REG_ADDRESS_F_CONTROL_SET_K, &twipr_firmware.control, &TWIPR_ControlManager::setBalancingGain);

/* Set Direct Input Register Entry */
core_utils_RegisterEntry<void, twipr_control_direct_input_t> reg_set_direct(&register_map, REG_ADDRESS_F_CONTROL_SET_DIRECT_INPUT, &twipr_firmware.control, &TWIPR_ControlManager::setDirectInput);

/* Set Balancing Input Register Entry */
core_utils_RegisterEntry<void, twipr_balancing_control_input_t> reg_set_balancing(&register_map, REG_ADDRESS_F_CONTROL_SET_BALANCING_INPUT, &twipr_firmware.control, &TWIPR_ControlManager::setBalancingInput);

/* Set Speed Input Register Entry */
core_utils_RegisterEntry<void, twipr_speed_control_input_t> reg_set_speed(&register_map, REG_ADDRESS_F_CONTROL_SET_SPEED_INPUT, &twipr_firmware.control, &TWIPR_ControlManager::setSpeed);

/* Set PID Forward Register Entry */
core_utils_RegisterEntry<uint8_t, float[3]> reg_set_pid_fwd(&register_map, REG_ADDRESS_F_CONTROL_SET_FORWARD_PID, &twipr_firmware.control, &TWIPR_ControlManager::setVelocityControlForwardPID);

/* Set PID Turn Register Entry */
core_utils_RegisterEntry<uint8_t, float[3]> reg_set_pid_turn(&register_map, REG_ADDRESS_F_CONTROL_SET_TURN_PID, &twipr_firmware.control, &TWIPR_ControlManager::setVelocityControlTurnPID);

/* Get Control Configuration Register Entry */
core_utils_RegisterEntry<twipr_control_configuration_t, void> reg_get_ctrl_conf(&register_map, REG_ADDRESS_F_CONTROL_GET_CONFIGURATION, &twipr_firmware.control, &TWIPR_ControlManager::getControlConfiguration);

/* Sequencer */

/* Load Sequence Function Register Entry */
core_utils_RegisterEntry<bool, twipr_sequencer_sequence_data_t> reg_load_seq(&register_map, REG_ADDRESS_F_SEQUENCE_LOAD, &twipr_firmware.sequencer, &TWIPR_Sequencer::loadSequence);

/* Read Sequence Data Register Entry */
core_utils_RegisterEntry<twipr_sequencer_sequence_data_t, void> reg_read_seq(&register_map, REG_ADDRESS_F_SEQUENCE_READ, &twipr_firmware.sequencer, &TWIPR_Sequencer::readSequence);

/* Start Sequence Function Register Entry */
core_utils_RegisterEntry<void, uint16_t> reg_start_seq(&register_map, REG_ADDRESS_F_SEQUENCE_START, &twipr_firmware.sequencer, &TWIPR_Sequencer::startSequence);

/* Abort Sequence Function Register Entry */
core_utils_RegisterEntry<void, void> reg_abort_seq(&register_map, REG_ADDRESS_F_SEQUENCE_STOP, &twipr_firmware.sequencer, &TWIPR_Sequencer::abortSequence);

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
 * @brief Initializes and starts the firmware task.
 *
 * This is the entry point from the main function that spawns the firmware task.
 */
void firmware() {
    osThreadNew(start_firmware_task, (void*)&twipr_firmware, &firmware_task_attributes);
}

/**
 * @brief Task wrapper to execute the firmware's main task function.
 * @param argument Pointer to the firmware object.
 *
 * This function casts the argument to a TWIPR_Firmware pointer and calls the helperTask.
 */
void start_firmware_task(void* argument) {
    TWIPR_Firmware* firmware = (TWIPR_Firmware*)argument;
    // Start the helper task (core firmware loop)
    firmware->helperTask();
}

/**
 * @brief Constructor for TWIPR_Firmware.
 *
 * Constructor logic can be extended if necessary.
 */
TWIPR_Firmware::TWIPR_Firmware() {
    // Currently empty - add initialization if needed
}

/**
 * @brief Main firmware task logic.
 *
 * Initializes firmware components, provides feedback via buzzer and LEDs, then
 * enters the main loop for periodic control tasks.
 */
void TWIPR_Firmware::helperTask() {
    // Initialize firmware modules and configurations
    HAL_StatusTypeDef status;
    status = this->init();
    if (status) {
        // Halt if initialization fails
        while (true) { nop(); }
    }

    status = this->start();
    if (status) {
        // Halt if start fails
        while (true) { nop(); }
    }

    osDelay(150);

    // Signal successful initialization with a beep
    rc_buzzer.setConfig(900, 250, 1);
    rc_buzzer.start();

    // Initialize LED states
    rc_rgb_led_side_1.setColor(0, 0, 0);
    rc_rgb_led_side_1.state(1);

    rgb_color_struct_t color_white_dim = { .red = 2, .green = 2, .blue = 2 };
    extender.rgbLEDStrip_extern_setColor(color_white_dim);

    elapsedMillis debug_timer;

    // Main task loop
    while (true) {
        // Update control mode LED if timer exceeds 250ms
        if (this->timer_control_mode_led > 250) {
            this->timer_control_mode_led.reset();
            this->setControlModeLed();
        }

        // Debug timer reset every 1000ms
        if(debug_timer >= 1000) {
            debug_timer.reset();
        }
        osDelay(100);
    }
}

/**
 * @brief Initializes all firmware modules and configurations.
 *
 * Sets up robot control, peripherals, communication, sensors, estimation,
 * control, drive, safety, sequencer, and logging modules.
 *
 * @return HAL_OK if initialization succeeds, or an error status.
 */
HAL_StatusTypeDef TWIPR_Firmware::init() {
    // Initialize robot control and peripheral modules
    robot_control_init();
    robot_control_start();
    io_start();

    // Setup RGB LED and buzzer for feedback
    rc_rgb_led_status.setColor(120, 40, 0); // Orange color indicates startup
    rc_rgb_led_status.state(1);
    rc_buzzer.setConfig(800, 250, 1);
    rc_buzzer.start();
    osDelay(250); // Allow peripherals to initialize

    // Communication module configuration
    twipr_communication_config_t twipr_comm_config = {
        .huart = BOARD_CM4_UART,
        .hspi = BOARD_SPI_CM4,
        .sample_notification_gpio = core_utils_GPIO(CM4_SAMPLE_NOTIFICATION_PORT, CM4_SAMPLE_NOTIFICATION_PIN),
        .sequence_rx_buffer = this->sequencer.rx_buffer,
        .len_sequence_buffer = TWIPR_SEQUENCE_BUFFER_SIZE,
        .reset_uart_exti = CM4_UART_RESET_EXTI,
    };
    this->comm.init(twipr_comm_config);
    this->comm.start();

    // Sensors initialization
    twipr_sensors_config_t twipr_sensors_config = { .drive = &this->drive };
    this->sensors.init(twipr_sensors_config);

    // Estimation module configuration
    twipr_estimation_config_t twipr_estimation_config = {
        .drive = &this->drive,
        .sensors = &this->sensors,
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

    // Drive configuration
    twipr_drive_can_config_t twipr_drive_config = {
        .can = &this->comm.can,
        .id_left = 1,
        .id_right = 2,
        .direction_left = -1,
        .direction_right = 1,
        .torque_max = 0.4
    };
    HAL_StatusTypeDef status = this->drive.init(twipr_drive_config);
    if (status) {
        return status;
    }

    // Safety module initialization
    twipr_supervisor_config_t supervisor_config = {
        .estimation = &this->estimation,
        .drive = &this->drive,
        .control = &this->control,
        .communication = &this->comm,
        .off_button = &off_button,
        .max_wheel_speed = TWIPR_SAFETY_MAX_WHEEL_SPEED,
    };
    this->supervisor.init(supervisor_config);

    // Sequencer module setup
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

    // Initialize debug data
    this->debugData = twipr_debug_sample_t{0};
    this->debugData.debug2 = 55;

    return HAL_OK;
}

/**
 * @brief Starts the firmware components and control tasks.
 *
 * This function starts sensors, estimation, drive, control, safety,
 * sequencer modules, and creates the control task.
 *
 * @return HAL_OK if all modules start successfully.
 */
HAL_StatusTypeDef TWIPR_Firmware::start() {
    // Start sensors and estimation modules
    this->sensors.start();
    this->estimation.start();

    HAL_StatusTypeDef status = this->drive.start();
    if (status) {
        while(true) { nop(); }
    }

    // Start control and safety modules
    this->control.start();
    this->supervisor.start();

    // Start sequencer module
    this->sequencer.start();

    // Create the control task thread
    osThreadNew(start_firmware_control_task, (void*)&twipr_firmware, &control_task_attributes);

    // Set firmware state to running
    this->firmware_state = TWIPR_FIRMWARE_STATE_RUNNING;
    return HAL_OK;
}

/**
 * @brief Main control task function for the firmware.
 *
 * Ensures periodic execution of control logic and handles errors.
 * It measures loop time and triggers error handling if the loop overruns.
 */
void TWIPR_Firmware::controlTask() {
    uint32_t global_tick;  // Current system tick
    uint32_t loop_time;    // Duration of one control loop

    while (true) {
        global_tick = osKernelGetTickCount();  // Record start tick

        // Execute a single control step
        this->controlTaskStep();

        // Calculate elapsed time for the loop
        loop_time = osKernelGetTickCount() - global_tick;

        // If loop time exceeds allowed period, flag an error
        if (loop_time > (1000.0 / (float)TWIPR_CONTROL_TASK_FREQ)) {
            this->firmware_state = TWIPR_FIRMWARE_STATE_ERROR;
            this->error = TWIPR_ERROR_CRITICAL;
        }

        // Delay until next cycle
        osDelayUntil(global_tick + (uint32_t)(1000.0 / (float) TWIPR_CONTROL_TASK_FREQ));
    }
}

/**
 * @brief Performs a single step of the control logic.
 *
 * Updates the system state, checks safety, updates sequencer and control,
 * collects logging samples, and sets status LED colors.
 */
void TWIPR_Firmware::controlTaskStep() {
    switch (this->firmware_state) {
        case TWIPR_FIRMWARE_STATE_RUNNING: {
            // Toggle activity LED every 250ms
            if (activityTimer > 250) {
                activityTimer.reset();
                rc_activity_led.toggle();
            }

            // Check safety module for errors
            twipr_error_t error = this->supervisor.check();
            if (!(error == TWIPR_ERROR_NONE)) {
                this->errorHandler(error);
            }

            // Update sequencer and control modules
            this->sequencer.update();
            this->control.update();

            // Collect and send logging samples if buffer is full
            sample_buffer_state = this->logging.collectSamples();
            if (sample_buffer_state == TWIPR_LOGGING_BUFFER_FULL) {
                this->comm.provideSampleData(this->logging.sample_buffer);
            }

            // Increment firmware tick counter
            this->tick++;

            // Set status LED to green indicating normal operation
            rc_rgb_led_status.setColor(0, 60, 0);
            break;
        }
        case TWIPR_FIRMWARE_STATE_ERROR: {
            // Set LED to red in error state
            rc_rgb_led_status.setColor(120, 0, 0);
            break;
        }
        default: {
            // Fallback for undefined states
            rc_rgb_led_status.setColor(120, 0, 0);
            break;
        }
    }
}

/**
 * @brief Handles firmware errors.
 *
 * Stops control if a critical error occurs.
 * @param error The error code to process.
 */
void TWIPR_Firmware::errorHandler(twipr_error_t error) {
    switch (error) {
        case TWIPR_ERROR_CRITICAL: {
            this->control.stop();
            this->firmware_state = TWIPR_FIRMWARE_STATE_ERROR;
            break;
        }
        case TWIPR_ERROR_WARNING: {
            // Warning: Additional handling can be added here
            break;
        }
        case TWIPR_ERROR_NONE: {
            // No error; no action needed
            break;
        }
    }
}

/**
 * @brief Wrapper function to start the control task.
 *
 * This function casts the argument to a firmware pointer and calls controlTask().
 * @param argument Pointer to the firmware object.
 */
void start_firmware_control_task(void* argument) {
    TWIPR_Firmware* firmware = (TWIPR_Firmware*)argument;
    firmware->controlTask();
}

/**
 * @brief Retrieves a logging sample with the current firmware state.
 *
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
 * @brief Updates the side LED color based on the current control mode.
 *
 * Changes the LED color to represent:
 * - Red: OFF mode
 * - Amber: Balancing mode
 * - Green: Velocity mode
 */
void TWIPR_Firmware::setControlModeLed() {
    if (this->control.mode == TWIPR_CONTROL_MODE_OFF) {
        rc_rgb_led_side_1.setColor(100, 0, 0); // Red for OFF mode
    } else if (this->control.mode == TWIPR_CONTROL_MODE_BALANCING) {
        rc_rgb_led_side_1.setColor(100, 70, 0); // Amber for balancing
    } else if (this->control.mode == TWIPR_CONTROL_MODE_VELOCITY) {
        rc_rgb_led_side_1.setColor(0, 100, 0); // Green for velocity mode
    }
}

/**
 * @brief Debug function used for custom debugging operations.
 *
 * @param input The debug input value to process.
 * @return Processed debug value.
 */
uint8_t TWIPR_Firmware::debug(uint8_t input) {
    // Increment input for debugging purposes (custom logic can be added)
    return input + 1;
}
