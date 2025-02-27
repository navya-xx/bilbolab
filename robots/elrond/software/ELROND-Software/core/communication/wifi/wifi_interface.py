from core.communication.protocol import Protocol
from core.communication.wifi.tcp.protocols.tcp_json_protocol import TCP_JSON_Protocol, TCP_JSON_Message
from core.communication.wifi.wifi_connection import WIFI_Connection
from core.communication.wifi.data_link import DataLink, Command, generateDataDict, generateCommandDict, CommandArgument
from utils.callbacks import Callback, callback_handler, CallbackContainer
from utils.events import event_handler
from utils.logging_utils import Logger

# === GLOBAL VARIABLES =================================================================================================
logger = Logger("WIFI INTERFACE")


# ======================================================================================================================
@callback_handler
class WIFI_Interface_Callbacks:
    connected: CallbackContainer
    disconnected: CallbackContainer
    sync: CallbackContainer


@event_handler
class WIFI_Interface_Events:
    ...


class Stream:
    parameters: list
    connection: object
    interval: float


# ======================================================================================================================
class WIFI_Interface:
    name: str
    id: str
    device_class: str
    device_type: str
    device_revision: str

    uid: bytes
    data: dict[str, (dict, DataLink)]
    commands: dict[str, (dict, Command)]

    connection: WIFI_Connection

    # streams: list[Stream]  # TODO: Could be removed. Not used

    connected: bool

    callbacks: WIFI_Interface_Callbacks

    protocol: Protocol = TCP_JSON_Protocol

    # === INIT =========================================================================================================
    def __init__(self, interface_type: str = 'wifi', device_class: str = None, device_type: str = None,
                 device_revision: str = None,
                 device_name: str = None, device_id: str = None):
        # Read the device config file

        self.device_class = device_class
        self.device_type = device_type
        self.device_revision = device_revision
        self.name = device_name
        self.id = device_id
        self.connected = False

        self.callbacks = WIFI_Interface_Callbacks()
        self.connection = WIFI_Connection(id=device_id)

        # Configure the WI-FI connection
        self.connection.callbacks.connected.register(self._connected_callback)
        self.connection.callbacks.disconnected.register(self._disconnected_callback)
        self.connection.callbacks.rx.register(self._rx_callback)

        # --- PARAMETERS ---
        # Set up the parameters (should be filled with DataLink objects or groups of DataLink objects)
        self.data = {}  # TODO: Populate parameters for this board

        # --- COMMANDS ---
        self.commands = {}
        # Register the getCommands command to return all registered commands with their descriptions.
        self.addCommand("getCommands", self.getCommands, [], "Return the description of all registered commands and their arguments.")

    # === PUBLIC METHODS ================================================================================================
    def start(self):
        logger.debug("Start WIFI Interface")
        self.connection.start()

    # ------------------------------------------------------------------------------------------------------------------
    def close(self):
        self.connection.close()

    # ------------------------------------------------------------------------------------------------------------------
    def sendEventMessage(self, event: str, data: dict = None, request_id: int = None):
        """
        Helper function to send event messages back to the remote.
        """
        msg = TCP_JSON_Message()
        msg.source = self.id
        msg.address = ''
        msg.type = 'event'
        msg.data = {'event': event}
        msg.data.update(data)
        if request_id is not None:
            msg.request_id = request_id
        self._wifi_send(msg)

    # ------------------------------------------------------------------------------------------------------------------
    def sendStreamMessage(self, data):
        msg = TCP_JSON_Message()
        msg.source = self.id
        msg.address = 0
        msg.type = 'stream'
        msg.data = data

        self._wifi_send(msg)

    # ------------------------------------------------------------------------------------------------------------------
    def addCommands(self, commands):
        if isinstance(commands, Command):
            self.commands[commands.identifier] = commands
        elif isinstance(commands, list):
            assert all(isinstance(command, Command) for command in commands)
            for command in commands:
                self.commands[command.identifier] = command
        elif isinstance(commands, dict):
            for command_identifier, command in commands.items():
                assert (isinstance(command, Command))
                self.commands[command_identifier] = command

    # ------------------------------------------------------------------------------------------------------------------
    def addCommand(self, identifier: str, callback: (callable, Callback), arguments: list[(str, CommandArgument)], description: str):
        self.commands[identifier] = Command(identifier=identifier, callback=callback, arguments=arguments,
                                            description=description)

    # ------------------------------------------------------------------------------------------------------------------
    def getCommands(self):
        """
        Returns a dictionary description of all registered commands.
        """
        return generateCommandDict(self.commands)

    # === PRIVATE METHODS =============================================================================================
    def _wifi_send(self, message):
        self.connection.send(message)

    # ------------------------------------------------------------------------------------------------------------------
    def _connected_callback(self):
        self._sendDeviceIdentification()
        self.connected = True
        for callback in self.callbacks.connected:
            callback(self)

    # ------------------------------------------------------------------------------------------------------------------
    def _disconnected_callback(self):
        self.connected = False
        for callback in self.callbacks.disconnected:
            callback(self)

    # ------------------------------------------------------------------------------------------------------------------
    def _rx_callback(self, message, *args, **kwargs):
        # Handle the message
        self._handleRxMessage(message)

    # ------------------------------------------------------------------------------------------------------------------
    def _handleRxMessage(self, message: TCP_JSON_Message):
        # Handle the message based on its type
        if message.type == 'write':
            self._handler_writeMessage(message)
        elif message.type == 'read':
            self._handler_readMessage(message)
        elif message.type == 'function':
            self._handler_functionMessage(message)
        elif message.type == 'event':
            self._handlerEventMessage(message)

    # ------------------------------------------------------------------------------------------------------------------
    def _handler_writeMessage(self, message: TCP_JSON_Message):
        """
        Processes write messages by setting parameters. If errors occur (invalid parameter name,
        value out of bounds, etc.) an event message or response is sent back.
        """
        errors = {}

        for entry, value in message.data.items():
            if entry not in self.data:
                logger.warning(f"Received parameter {entry}, which is not a valid entry.")
                errors[entry] = "Invalid parameter"
                continue

            param = self.data[entry]
            # Handle single parameter
            if isinstance(param, DataLink):
                try:
                    if not param.set(value):
                        errors[entry] = f"Failed to set parameter {entry}"
                        logger.warning(f"Failed to set parameter {entry} to value {value}.")
                    else:
                        logger.debug(f"Set parameter {entry} to value {value}.")
                except Exception as e:
                    errors[entry] = str(e)
                    logger.error(f"Exception setting parameter {entry}: {e}")
            # Handle group of parameters (only one level supported)
            elif isinstance(param, dict) and isinstance(value, dict):
                for sub_entry, sub_value in value.items():
                    if sub_entry not in param:
                        logger.warning(f"Received parameter {entry}:{sub_entry}, which is not a valid entry.")
                        errors[f"{entry}:{sub_entry}"] = "Invalid sub-parameter"
                        continue
                    sub_param = param[sub_entry]
                    if not isinstance(sub_param, DataLink):
                        logger.warning(f"Cannot set parameter {entry}:{sub_entry}: unsupported parameter structure.")
                        errors[f"{entry}:{sub_entry}"] = "Invalid parameter structure"
                        continue
                    try:
                        if not sub_param.set(sub_value):
                            logger.warning(f"Failed to set parameter {entry}:{sub_entry} to value {sub_value}.")
                            errors[f"{entry}:{sub_entry}"] = f"Failed to set parameter {sub_entry}"
                        else:
                            logger.debug(f"Set parameter {entry}:{sub_entry} to value {sub_value}.")
                    except Exception as e:
                        errors[f"{entry}:{sub_entry}"] = str(e)
                        logger.error(f"Exception setting parameter {entry}:{sub_entry}: {e}")
            else:
                logger.warning(f"Parameter {entry} has unsupported structure.")
                errors[entry] = "Unsupported parameter structure"

        if message.request_response:
            response_msg = TCP_JSON_Message()
            response_msg.source = self.id
            response_msg.address = ''
            response_msg.type = 'response'
            response_msg.request_id = message.id
            response_msg.data = {"success": len(errors) == 0, "errors": errors}
            self._wifi_send(response_msg)
        elif errors:
            # If no response is explicitly requested, still send an event for the errors.
            self.sendEventMessage("write_error", {"errors": errors}, request_id=message.id)

    # ------------------------------------------------------------------------------------------------------------------
    def _handler_readMessage(self, message: TCP_JSON_Message):
        """
        Processes read messages. If no specific parameters are provided, it returns all.
        If a parameter (or group) is not found or an error occurs during retrieval,
        an error is returned.
        """
        response = {}
        errors = {}

        # If no specific parameter is requested, read all parameters.
        if not message.data:
            for key, param in self.data.items():
                if isinstance(param, DataLink):
                    try:
                        response[key] = param.get()
                    except Exception as e:
                        errors[key] = str(e)
                        logger.error(f"Error reading parameter {key}: {e}")
                elif isinstance(param, dict):
                    response[key] = {}
                    for subkey, sub_param in param.items():
                        if isinstance(sub_param, DataLink):
                            try:
                                response[key][subkey] = sub_param.get()
                            except Exception as e:
                                errors[f"{key}:{subkey}"] = str(e)
                                logger.error(f"Error reading parameter {key}:{subkey}: {e}")
                        else:
                            errors[f"{key}:{subkey}"] = "Invalid parameter structure"
                else:
                    errors[key] = "Unsupported parameter structure"
        else:
            # Determine the keys to read based on the type of message.data
            if isinstance(message.data, dict):
                keys_to_read = message.data.keys()
            elif isinstance(message.data, list):
                keys_to_read = message.data
            else:
                keys_to_read = [message.data]

            for key in keys_to_read:
                if key not in self.data:
                    errors[key] = "Invalid parameter"
                    logger.warning(f"Received read request for invalid parameter {key}.")
                    continue
                param = self.data[key]
                if isinstance(param, DataLink):
                    try:
                        response[key] = param.get()
                    except Exception as e:
                        errors[key] = str(e)
                        logger.error(f"Error reading parameter {key}: {e}")
                elif isinstance(param, dict):
                    response[key] = {}
                    # If message.data is dict and provides a list of subkeys, use it; otherwise read all subkeys.
                    subkeys = None
                    if isinstance(message.data, dict) and isinstance(message.data.get(key, None), list):
                        subkeys = message.data[key]
                    if subkeys is None:
                        for subkey, sub_param in param.items():
                            if isinstance(sub_param, DataLink):
                                try:
                                    response[key][subkey] = sub_param.get()
                                except Exception as e:
                                    errors[f"{key}:{subkey}"] = str(e)
                                    logger.error(f"Error reading parameter {key}:{subkey}: {e}")
                            else:
                                errors[f"{key}:{subkey}"] = "Invalid parameter structure"
                    else:
                        for subkey in subkeys:
                            if subkey not in param:
                                errors[f"{key}:{subkey}"] = "Invalid sub-parameter"
                                logger.warning(f"Received read request for invalid sub-parameter {key}:{subkey}.")
                                continue
                            sub_param = param[subkey]
                            if isinstance(sub_param, DataLink):
                                try:
                                    response[key][subkey] = sub_param.get()
                                except Exception as e:
                                    errors[f"{key}:{subkey}"] = str(e)
                                    logger.error(f"Error reading parameter {key}:{subkey}: {e}")
                            else:
                                errors[f"{key}:{subkey}"] = "Invalid parameter structure"
                else:
                    errors[key] = "Unsupported parameter structure"
                    logger.warning(f"Parameter {key} has unsupported structure.")

        response_msg = TCP_JSON_Message()
        response_msg.source = self.id
        response_msg.address = ''
        response_msg.type = 'response'
        response_msg.request_id = message.id
        response_msg.data = {"output": response, "errors": errors, "success": len(errors) == 0}
        self._wifi_send(response_msg)

    # ------------------------------------------------------------------------------------------------------------------
    def _handler_functionMessage(self, message: TCP_JSON_Message):
        # Check for the function name
        if 'function' not in message.data:
            logger.warning("Received function message without function name")
            return

        function_name = message.data['function']

        # Check if the function is in the commands
        if function_name not in self.commands:
            logger.warning(f"Received function {function_name}, which is not a valid entry.")
            self.sendEventMessage("function_error", {"error": f"Function {function_name} not found"}, request_id=message.id)
            return

        # Check if 'input' is in the data
        if 'input' not in message.data:
            logger.warning(f"Received function {function_name} without input")
            self.sendEventMessage("function_error", {"error": f"Missing input for function {function_name}"}, request_id=message.id)
            return

        value = message.data['input']

        output = None
        error = None

        try:
            output = self.commands[function_name].execute(value)
            success = True
        except Exception as e:
            logger.warning(f"Error executing function {function_name}: {e}")
            success = False
            error = str(e)

        if message.request_response is not None:
            # Send a response message since a response was requested.
            response_message = TCP_JSON_Message()
            response_message.address = ''
            response_message.source = ''
            response_message.type = 'response'
            response_message.request_id = message.id
            response_message.data['output'] = output
            response_message.data['error'] = error
            response_message.data['success'] = success

            self._wifi_send(response_message)

    # ------------------------------------------------------------------------------------------------------------------
    def _handlerEventMessage(self, message):
        if message.data['event'] == 'sync':
            for callback in self.callbacks.sync:
                callback(message.data)
        # TODO: Add response if needed

    # ------------------------------------------------------------------------------------------------------------------
    def _sendDeviceIdentification(self):
        msg = TCP_JSON_Message()
        msg.source = self.id
        msg.address = ''
        msg.type = 'event'

        msg.data = {
            'event': 'device_identification',
            'device_class': self.device_class,
            'device_type': self.device_type,
            'device_name': self.name,
            'device_id': self.id,
            'address': self.id,
            'revision': self.device_revision,
            'data': generateDataDict(self.data),
            'commands': generateCommandDict(self.commands)
        }

        self._wifi_send(msg)
