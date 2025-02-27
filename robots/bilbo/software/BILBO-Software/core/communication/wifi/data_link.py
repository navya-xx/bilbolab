from utils.callbacks import Callback
from utils.logging_utils import Logger
import dataclasses
import inspect

logger = Logger("DATALINK")
# ======================================================================================================================

class DataLink:
    identifier: str  # Descriptor of the parameter which can be accessed from remote
    description: str  # Description of the parameter which will be shown when generating a list of parameters
    datatype: (tuple, type)  # Allowed datatypes for the parameter
    limits: list  # Allowed values
    limits_mode: str  # Can be either 'range' or 'explicit' for the values given in limits
    writable: bool  # If 'false', this parameter cannot be written
    write_function: Callback
    read_function: Callback
    index: int
    obj: object  # Object which the parameter is associated to
    name: str  # Name of the parameter in the object obj

    # === INIT =========================================================================================================
    def __init__(self, identifier, description, datatype, limits: list = None, limits_mode: str = 'range',
                 write_function: (Callback, callable) = None, read_function: (Callback, callable) = None,
                 obj: object = None, name: str = None, writable: bool = True, index: int = None):
        self.identifier = identifier
        self.description = description
        self.datatype = datatype
        self.limits = limits
        self.limits_mode = limits_mode
        self.write_function = write_function
        self.read_function = read_function
        self.obj = obj
        self.name = name
        self.writable = writable
        self.index = index

    # ------------------------------------------------------------------------------------------------------------------
    def get(self):
        if self.read_function is not None:
            return self.read_function()
        elif self.obj is not None and self.name is not None:
            if isinstance(self.obj, dict):
                return self.obj[self.name]
            else:
                return getattr(self.obj, self.name)

    # ------------------------------------------------------------------------------------------------------------------
    def set(self, value) -> bool:

        if not self.writable:
            return False

        # Check if the datatype is ok
        if not isinstance(value, self.datatype):
            # Exception for float and int:
            if self.datatype == float and isinstance(value, int):
                value = float(value)
            else:
                return False

        # Check if the limits are ok
        if self.limits is not None:
            if self.limits_mode == 'explicit':
                if value not in self.limits:
                    return False
            elif self.limits_mode == 'range':
                if value < self.limits[0] or value > self.limits[1]:
                    return False

        if self.obj is not None and self.name is not None:
            if isinstance(self.obj, dict):
                self.obj[self.name] = value
            else:
                setattr(self.obj, self.name, value)
        elif self.obj is not None and self.index is not None:
            self.obj[self.index] = value

        if self.write_function is not None:
            if not isinstance(self.write_function, Callback) and not hasattr(self.write_function, '__self__'):
                return self.write_function(self.obj, value)
            return self.write_function(value)

        return True

    # ------------------------------------------------------------------------------------------------------------------
    def generateDescription(self):
        out = {
            'identifier': self.identifier,
            'description': self.description,
            'datatype': str(self.datatype),
            'limits': self.limits,
            'writable': self.writable,
            'value': self.get()
        }
        return out


# ======================================================================================================================
@dataclasses.dataclass
class CommandArgument:
    name: str
    description: str
    type: type
    optional: bool = False
    default: any = None


# ----------------------------------------------------------------------------------------------------------------------
class Command:
    identifier: str
    callback: (callable, Callback)
    arguments: dict  # dict of CommandArgument objects with the key being the argument name
    description: str

    def __init__(self, identifier: str, callback: (callable, Callback), arguments, description: str):
        self.identifier = identifier
        self.callback = callback
        self.description = description

        # If 'arguments' is provided as a dict, use it directly.
        # If it's a list, convert it into a dict.
        if isinstance(arguments, dict):
            self.arguments = arguments
        elif isinstance(arguments, list):
            arg_dict = {}
            for item in arguments:
                if isinstance(item, str):
                    # Create a CommandArgument with the given name.
                    # datatype=object makes every type check pass, and optional is False.
                    arg_dict[item] = CommandArgument(name=item, description=item, type=object, optional=False)
                elif isinstance(item, CommandArgument):
                    arg_dict[item.name] = item
                else:
                    logger.error(f"Unsupported argument type in initialization: {item}")
            self.arguments = arg_dict
        else:
            logger.error("Unsupported type for arguments in Command initialization. Expected dict or list.")
            self.arguments = {}

    # ------------------------------------------------------------------------------------------------------------------
    def execute(self, arguments=None):
        if arguments is None:
            arguments = {}

        # If arguments is provided as a list, convert it into a dict using the order of self.arguments keys.
        if not isinstance(arguments, dict):
            if isinstance(arguments, list):
                new_args = {}
                keys = list(self.arguments.keys())
                for i, value in enumerate(arguments):
                    if i < len(keys):
                        new_args[keys[i]] = value
                arguments = new_args
            else:
                logger.error("Arguments provided to execute must be a dict or list.")
                arguments = {}

        final_args = {}

        # Check if all expected arguments are provided, and use default values where needed.
        for arg_name, command_arg in self.arguments.items():
            if arg_name in arguments:
                final_args[arg_name] = arguments[arg_name]
            else:
                if command_arg.optional:
                    if command_arg.default is not None:
                        final_args[arg_name] = command_arg.default
                    else:
                        # Attempt to retrieve default from the callback's signature
                        func = self.callback.function if isinstance(self.callback, Callback) else self.callback
                        try:
                            sig = inspect.signature(func)
                            param = sig.parameters.get(arg_name)
                            if param and param.default is not inspect.Parameter.empty:
                                final_args[arg_name] = param.default
                            else:
                                final_args[arg_name] = None
                        except Exception as e:
                            logger.error(f"Could not inspect callback for command {self.identifier}: {e}")
                            final_args[arg_name] = None
                else:
                    logger.error(f"Missing required argument '{arg_name}' for command {self.identifier}")
                    return

        # Execute the command with the collected arguments.
        if isinstance(self.callback, Callback):
            return self.callback(**final_args)
        else:
            return self.callback(**final_args)

    # ------------------------------------------------------------------------------------------------------------------
    def generateDescription(self):
        out = {
            'identifier': self.identifier,
            'description': self.description,
            'arguments': {arg_name: self._serialize_command_argument(arg) for arg_name, arg in self.arguments.items()}
        }
        return out

    # Helper method to convert the type in CommandArgument to a string
    def _serialize_command_argument(self, arg: CommandArgument) -> dict:
        arg_dict = dataclasses.asdict(arg)
        if 'type' in arg_dict:
            arg_dict['type'] = arg_dict['type'].__name__ if hasattr(arg_dict['type'], '__name__') else str(arg_dict['type'])
        return arg_dict


# ======================================================================================================================
def generateDataDict(data: dict[str, DataLink]):
    out = {}
    for name, value in data.items():
        if isinstance(value, DataLink):
            out[name] = value.generateDescription()
        elif isinstance(value, dict):
            out[name] = generateDataDict(value)
    return out


# ======================================================================================================================
def generateCommandDict(commands: dict[str, Command]):
    out = {}
    for name, command in commands.items():
        out[name] = command.generateDescription()
    return out
