import dataclasses
import os
import re
import shlex
import utils.colors as colors
import utils.string as string
from utils.callbacks import Callback
from utils.logging_utils import Logger

logger = Logger('CLI')
logger.setLevel("INFO")
os.system("")


@dataclasses.dataclass
class CommandArgument:
    name: str
    type: type
    array_size: int = 0
    short_name: str = None
    original_name: str = None
    description: str = None
    default: object = None
    optional: bool = False
    is_flag: bool = False

    def __post_init__(self):
        if self.short_name is None:
            self.short_name = self.name


class Command:
    description: str
    name: str
    arguments: dict[str, CommandArgument] = None
    callback: Callback

    def __init__(self,
                 name,
                 callback=None,
                 description='',
                 arguments: list[CommandArgument] = None,
                 allow_positionals=False,
                 **kwargs):

        self.name = name
        self.logger = Logger(f"Command \"{self.name}\"")
        self.description = description
        self.allow_positionals = allow_positionals
        self.callback = callback

        if not hasattr(self, 'arguments') or self.arguments is None:
            self.arguments = {}

        if arguments is not None:
            for argument in arguments:
                self.arguments[argument.name] = argument

    def function(self, *args, **kwargs):
        if self.callback is not None:
            return self.callback(*args, **kwargs)

    def run(self, command_input):
        # Parse the string or token list.
        arguments = self._parseString(command_input)
        if arguments is None:
            return

        positional_args = arguments[0]
        keyword_args = arguments[1]

        if self.allow_positionals:
            # Get the list of defined argument names in insertion order.
            arg_names = list(self.arguments.keys())
            if len(positional_args) > len(arg_names):
                self.logger.error(
                    f"Too many positional arguments provided. Expected at most {len(arg_names)} but got {len(positional_args)}.")
                return

            for i, pos in enumerate(positional_args):
                arg_name = arg_names[i]
                # Check if this argument is also provided as a keyword.
                if arg_name in keyword_args:
                    self.logger.error(f"Argument '{arg_name}' provided both positionally and as a keyword.")
                    return
                arg_def = self.arguments[arg_name]
                try:
                    # Attempt to convert the positional argument to the expected type.
                    cast_value = arg_def.type(pos)
                except Exception:
                    self.logger.error(
                        f"Type mismatch for argument '{arg_name}': expected {arg_def.type.__name__} but got value '{pos}'.")
                    return
                # Insert the cast value into the keyword_args dictionary.
                keyword_args[arg_name] = cast_value
            # Clear positional_args since they have been consumed.
            positional_args = []

        # Fill in missing optional/default/flag arguments.
        for name, argument in self.arguments.items():
            if argument.optional or argument.default is not None:
                if argument.name not in keyword_args.keys():
                    keyword_args[argument.name] = argument.default
            elif argument.is_flag:
                if argument.name not in keyword_args.keys():
                    keyword_args[argument.name] = False
            else:
                if argument.name not in keyword_args.keys():
                    self.logger.error(f"Argument \"{argument.name}\" was not provided")
                    return
        try:
            return self.function(*positional_args, **keyword_args)
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")

    def _parseString(self, command_input):
        # If the input is already a list (from shlex.split) then use it directly;
        # otherwise, split using a regex.
        if isinstance(command_input, list):
            tokens = command_input
        else:
            pattern = r'\[.*?\]|\'.*?\'|".*?"|\S+'
            tokens = re.findall(pattern, command_input)
        positional_args = []
        keyword_args = {}
        it = iter(tokens)

        for token in it:
            if token.startswith('--'):
                arg_name = token[2:]
                if arg_name not in self.arguments:
                    self.logger.error(f"Unknown argument: {arg_name}")
                    return None
                arg = self.arguments[arg_name]
                if arg.is_flag:
                    name = arg.original_name if arg.original_name is not None else arg.name
                    keyword_args[name] = True
                else:
                    try:
                        value = next(it)
                        if arg.array_size > 0:
                            match = re.match(r'\[(.*)\]', value)
                            if not match:
                                self.logger.error(f"Argument {arg_name} expects a list enclosed in brackets.")
                                return None
                            values = [v.strip() for v in match.group(1).split(',')]
                            if len(values) != arg.array_size:
                                self.logger.error(f"Argument {arg_name} expects a list of {arg.array_size} values.")
                                return None
                            name = arg.original_name if arg.original_name is not None else arg.name
                            keyword_args[name] = self._typecastArgument(self.arguments[arg_name], values)
                        else:
                            value = value.strip('"').strip("'")
                            name = arg.original_name if arg.original_name is not None else arg.name
                            keyword_args[name] = self._typecastArgument(self.arguments[arg_name], value)
                    except StopIteration:
                        self.logger.error(f"Argument {arg_name} expects a value.")
                        return None
                    except Exception as e:
                        self.logger.error(f"Error parsing argument {arg_name}: {e}")
                        return None
            elif token.startswith('-'):
                arg_short_name = token[1:]
                arg = next((a for a in self.arguments.values() if a.short_name == arg_short_name), None)
                if not arg:
                    self.logger.error(f"Unknown argument: {arg_short_name}")
                    return None
                if arg.is_flag:
                    name = arg.original_name if arg.original_name is not None else arg.name
                    keyword_args[name] = True
                else:
                    try:
                        value = next(it)
                        if arg.array_size > 0:
                            match = re.match(r'\[(.*)\]', value)
                            if not match:
                                self.logger.error(f"Argument {arg.name} expects a list enclosed in brackets.")
                                return None
                            values = [v.strip() for v in match.group(1).split(',')]
                            if len(values) != arg.array_size:
                                self.logger.error(f"Argument {arg.name} expects a list of {arg.array_size} values.")
                                return None
                            name = arg.original_name if arg.original_name is not None else arg.name
                            keyword_args[name] = self._typecastArgument(self.arguments[arg.name], values)
                        else:
                            value = value.strip('"').strip("'")
                            name = arg.original_name if arg.original_name is not None else arg.name
                            keyword_args[name] = self._typecastArgument(self.arguments[arg.name], value)
                    except StopIteration:
                        self.logger.error(f"Argument {arg.name} expects a value.")
                        return None
                    except Exception as e:
                        self.logger.error(
                            f"Error parsing value \"{value}\" for argument \"{arg.name}\" of type {arg.type}")
                        return None
            else:
                positional_args.append(token.strip('"').strip("'"))

        return positional_args, keyword_args

    def _typecastArgument(self, argument, value):
        try:
            if isinstance(value, list):
                return [argument.type(v) for v in value]
            return argument.type(value)
        except ValueError:
            raise ValueError(f"Cannot convert value \"{value}\" for argument {argument.name} to {argument.type}")

    def help(self):
        help_string = (f"{string.bold_text}Command:{string.text_reset} "
                       f"{string.escapeCode(text_color_rgb=colors.MEDIUM_CYAN)}"
                       f"{self.name}{string.text_reset}\n")
        help_string += f"{string.bold_text}Description:{string.text_reset} {self.description}\n"
        help_string += f"{string.bold_text}Arguments:{string.text_reset}"
        if len(self.arguments) > 0:
            help_string += "\n"
            for argument in self.arguments.values():
                help_string += f"{string.escapeCode(text_color_rgb=colors.DARK_CYAN)}  --{argument.name}{string.text_reset} ({argument.type.__name__})"
                if argument.short_name is not None:
                    help_string += f" (-{argument.short_name})"
                if argument.description:
                    help_string += f": {argument.description}"
                if argument.optional:
                    help_string += f" (Optional, default: {argument.default})"
                help_string += "\n"
        else:
            help_string += " -\n"
        return help_string


class CommandSet:
    commands: dict[str, Command]
    parent_set: (None, 'CommandSet')
    child_sets: (None, 'CommandSet')
    description: str = ''

    def __init__(self, name, commands: list[Command] = None, child_sets: list['CommandSet'] = None, description=''):
        self.commands = {}
        self.name = name
        self.description = description
        self.parent_set = None
        self.child_sets = {}

        self.logger = Logger(name=f'CommandSet {self.name}')

        if commands:
            for command in commands:
                self.addCommand(command)

        if child_sets:
            for child_set in child_sets:
                self.addChild(child_set)

        # Automatically add a help command to every set.
        self.addCommand(Command(
            name='help',
            description='Prints all available commands',
            arguments=[CommandArgument(
                name='detail',
                type=bool,
                short_name='d',
                is_flag=True,
                default=False
            )],
            callback=self.help
        ))

    def addCommand(self, command: Command):
        if isinstance(command, dict):
            for key, value in command.items():
                self.commands[value.name] = value
        elif isinstance(command, Command):
            self.commands[command.name] = command

    @property
    def commandSetPath(self):
        if self.parent_set is None:
            return self.name
        else:
            return f"{self.parent_set.commandSetPath}/{self.name}"

    def run(self, command_string):
        """
        Modified run method that supports:
          - A token '.' meaning to switch to the root set.
          - Leading '..' tokens meaning to go to the parent.
        """
        tokens = shlex.split(command_string)
        if not tokens:
            return

        current_set = self
        i = 0

        # Process leading special tokens '.' and '..'
        while i < len(tokens):
            token = tokens[i]
            if token == '.':
                # Go to the root set.
                while current_set.parent_set is not None:
                    current_set = current_set.parent_set
                i += 1
            elif token == '..':
                if current_set.parent_set is not None:
                    current_set = current_set.parent_set
                else:
                    self.logger.error("Already at root, cannot exit further.")
                    return
                i += 1
            else:
                break

        # Process remaining tokens: check for child sets or commands.
        while i < len(tokens):
            token = tokens[i]
            if token == '.':
                i += 1
                continue
            elif token in current_set.child_sets:
                current_set = current_set.child_sets[token]
                i += 1
            elif token in current_set.commands:
                cmd_name = token
                i += 1
                remaining_tokens = tokens[i:]
                x = current_set.commands[cmd_name].run(remaining_tokens)
                return x
            else:
                self.logger.error(f"Token '{token}' not recognized in set '{current_set.name}'")
                return

        return current_set

    def printCommand(self, command, args, params):
        print(f'{self.name.capitalize()} - Command: {command}')
        print(f'Arguments: {args}')
        print('Parameters:')
        for key, value in params.items():
            print(f'  {key}: {value}')

    def addChild(self, child_cli):
        self.child_sets[child_cli.name] = child_cli
        child_cli.parent_set = self

    def removeChild(self, child_cli):
        if isinstance(child_cli, CommandSet):
            self.child_sets.pop(child_cli.name)
        elif isinstance(child_cli, str):
            self.child_sets.pop(child_cli)

    def help(self, *args, detail=False, **kwargs):
        help_output = []

        if len(args) == 1:
            command = args[0]
            if command in self.commands.keys():
                help_output.append("-----------------------------------------")
                help_output.append(self.commands[command].help())
                help_output.append("-----------------------------------------")
            elif command in self.child_sets.keys():
                help_output.append("-----------------------------------------")
                help_output.append(self.child_sets[command].shortHelp())
                help_output.append("-----------------------------------------")
            else:
                self.logger.warning(f"Command {command} not found")

        elif len(args) == 0:
            help_output.append(
                f"Help for command set {string.escapeCode(text_color_rgb=colors.MEDIUM_MAGENTA, bold=True)}{self.commandSetPath}{string.text_reset}\n"
                f"use \"help --detail\" for more details"
            )
            help_output.append("-----------------------------------------")

            command_sets_overview_string = f"{string.escapeCode(colors.MEDIUM_MAGENTA, bold=True)}Command Sets: {string.text_reset}"
            if len(self.child_sets.keys()) > 0:
                for subset in self.child_sets.values():
                    command_sets_overview_string += f"{string.escapeCode(colors.MEDIUM_MAGENTA)}{subset.name}{string.text_reset}  "
            else:
                command_sets_overview_string += "-"
            help_output.append(command_sets_overview_string)

            if detail:
                help_output.append("-----------------------------------------")
                help_output.append(
                    "Enter command set name to enter. Type \"exit\" to exit to parent set, type \"EXIT\" to jump to root set."
                )
                help_output.append("-----------------------------------------")
                for child in self.child_sets.values():
                    help_output.append(child.shortHelp())

            help_output.append("-----------------------------------------")
            commands_overview_string = f"{string.escapeCode(colors.MEDIUM_CYAN, bold=True)}Commands: {string.text_reset}"
            if len(self.commands) > 1:
                for command in self.commands.values():
                    if command.name != 'help':
                        commands_overview_string += f"{string.escapeCode(colors.MEDIUM_CYAN)}{command.name}{string.text_reset} "
            else:
                commands_overview_string += "-"
            help_output.append(commands_overview_string)
            help_output.append("-----------------------------------------")

            if detail:
                help_output.append(
                    "Enter command and add keyword arguments by --name (-shortname). Arrays are denoted by [].")
                help_output.append("-----------------------------------------")
                if len(self.commands) > 1:
                    for command in self.commands.values():
                        if command.name != "help":
                            help_output.append(command.help())
                            help_output.append("-----------------------------------------")

        return "\n".join(help_output)

    def shortHelp(self):
        helpstring = ''
        helpstring += f"{string.bold_text}Command Set: {string.text_reset}{string.escapeCode(colors.MEDIUM_MAGENTA)}{self.name}{string.text_reset}\n"
        helpstring += f"{string.bold_text}Description: {string.text_reset} {self.description}\n"
        helpstring += f"{string.bold_text}Commands:{string.text_reset}  "
        for subset in self.child_sets.values():
            helpstring += f"{string.escapeCode(colors.MEDIUM_MAGENTA)}{subset.name}{string.text_reset}   "
        for command in self.commands.values():
            if command.name != 'help':
                helpstring += f"{string.escapeCode(colors.MEDIUM_CYAN)}{command.name}{string.text_reset}   "
        return helpstring

    @staticmethod
    def _parse(command_string):
        tokens = shlex.split(command_string)
        command = tokens[0]
        params = {}
        args = []
        i = 1
        while i < len(tokens):
            if tokens[i].startswith('-'):
                if tokens[i].startswith('--'):
                    key = tokens[i][2:]
                else:
                    key = tokens[i][1:]
                if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                    value = tokens[i + 1]
                    i += 1
                else:
                    value = None
                params[key] = value
            else:
                args.append(tokens[i])
            i += 1
        remaining_command_string = ' '.join(tokens[1:])
        return command, args, params, remaining_command_string


# ======================================================================================================================
class CLI:
    root_set: (None, CommandSet)
    active_set: (None, CommandSet)

    text_output_function: callable

    # ==================================================================================================================
    def __init__(self, root_set: CommandSet = None, active_set: CommandSet = None,
                 text_output_function: callable = None):

        self.text_output_function = text_output_function

        self.root_set = root_set
        if active_set is None:
            active_set = self.root_set
        self.setActiveSet(active_set)

    # ------------------------------------------------------------------------------------------------------------------
    def setRootSet(self, root_set: CommandSet):
        self.root_set = root_set
        if self.active_set is None:
            self.active_set = self.root_set

    # ------------------------------------------------------------------------------------------------------------------
    def setActiveSet(self, active_set: CommandSet):
        self.active_set = active_set

    # ------------------------------------------------------------------------------------------------------------------
    def runCommand(self, command: str):
        if self.active_set is None:
            return

        ret = self.active_set.run(command)
        if isinstance(ret, CommandSet):
            self.active_set = ret
        else:
            if isinstance(ret, str):
                self.trace(ret)
            return ret

    # ------------------------------------------------------------------------------------------------------------------
    def getCommandSetByPath(self, path: list) -> (None, CommandSet):
        """
        Helper method to retrieve a CommandSet by a given path.
        The path is a list of command-set names starting at the root.
        For example, given path ['.', 'set1', 'set2'], the method will start
        at the root and search for child sets 'set1' then 'set2'.
        """

        if self.root_set is None:
            return None

        current_set = self.root_set
        if not path:
            return current_set

        for token in path:
            # If the token is '.' or matches the current set's name, stay here.
            if token == '.' or token == current_set.name:
                continue
            elif token in current_set.child_sets:
                current_set = current_set.child_sets[token]
            else:
                logger.error(f"Command set token '{token}' not found in '{current_set.name}'")
                return None
        return current_set

    # ------------------------------------------------------------------------------------------------------------------
    def executeFromConnectorDict(self, command_dict: dict):
        """
        Executes a command using a dictionary with the structure:

            {
                'name': 'function1',
                'path': ['.', 'set1', 'set2'],
                'arguments': {
                    'positional': [],
                    'keyword': {'a': 2, 'b': 'HALLO'}
                }
            }

        The method will:
          1. Verify that the required keys ('name', 'path', 'arguments') are present.
          2. Use getCommandSetByPath() to locate the target command set.
          3. Check that the specified command exists within that set.
          4. Build a token list from the provided arguments and delegate parsing to the command.
        """
        # Validate required keys.
        required_keys = ['name', 'path', 'arguments']
        for key in required_keys:
            if key not in command_dict:
                logger.error(f"Command dictionary missing required key: {key}")
                return

        command_name = command_dict['name']
        command_path = command_dict['path']
        arguments = command_dict['arguments']

        pos_args = arguments.get('positional', [])
        kw_args = arguments.get('keyword', {})

        # Retrieve target command set using the provided path.
        target_set = self.getCommandSetByPath(command_path)
        if target_set is None:
            logger.error(f"Command set specified by path {command_path} not found.")
            return

        if command_name not in target_set.commands:
            logger.error(f"Command '{command_name}' not found in command set '{target_set.name}'.")
            return

        command_obj = target_set.commands[command_name]

        # Build a token list mimicking CLI input.
        tokens = []
        # Add all positional arguments.
        for pos in pos_args:
            tokens.append(str(pos))
        # Add keyword arguments.
        for key, value in kw_args.items():
            # Try to retrieve the corresponding argument definition.
            arg_def = command_obj.arguments.get(key)
            if arg_def is None:
                # If not found, check if any argument has this as its original_name.
                for a in command_obj.arguments.values():
                    if a.original_name == key:
                        arg_def = a
                        break
            if arg_def is not None and arg_def.is_flag:
                if value:
                    tokens.append(f"--{arg_def.name}")
            else:
                tokens.append(f"--{key}")
                tokens.append(str(value))
        # Delegate parsing and execution to the command's run method.
        try:
            ret = command_obj.run(tokens)
            if isinstance(ret, str):
                self.trace(ret)
            return ret
        except Exception as e:
            logger.error(f"Error executing command '{command_name}': {e}")
            self.trace(f"Error executing command '{command_name}': {e}")

    # ------------------------------------------------------------------------------------------------------------------
    def getCommandSetDescription(self):
        def serialize_command(command: Command):
            return {
                "name": command.name,
                "description": command.description,
                "arguments": {
                    arg_name: {
                        "type": arg.type.__name__,
                        "array_size": arg.array_size,
                        "short_name": arg.short_name,
                        "original_name": arg.original_name,
                        "description": arg.description,
                        "default": arg.default,
                        "optional": arg.optional,
                        "is_flag": arg.is_flag,
                    } for arg_name, arg in command.arguments.items()
                }
            }

        # --------------------------------------------------------------------------------------------------------------
        def serialize_command_set(command_set: CommandSet):
            return {
                "name": command_set.name,
                "description": command_set.description,
                "commands": {cmd_name: serialize_command(cmd) for cmd_name, cmd in command_set.commands.items()},
                "child_sets": {child_name: serialize_command_set(child) for child_name, child in
                               command_set.child_sets.items()}
            }

        return serialize_command_set(self.root_set)

    # ------------------------------------------------------------------------------------------------------------------
    def trace(self, text):
        if self.text_output_function is not None:
            self.text_output_function(text)


# ======================================================================================================================
class CLI_Connector:
    """
    A CLI mirror intended to run in a separate process communicating via websocket/json.
    It works with a serialized command set (a dict tree as returned by CLI.getCommandSetDescription())
    and exposes a single method `parseCommand` that returns a dict with:

        {
            'success': True,
            'type': 'change_set' or 'command',
            'command': {     # only for type 'command'
                'name': 'function1',
                'path': ['root','set1','set1_1'],
                'arguments': {
                    'positional': [...],
                    'keyword': { ... }
                }
            },
            'active_set': ['root','set1']  # current active set path
        }

    Special tokens:
      - A command starting with '.' is treated as absolute (from the root).
      - A token '..' means to move to the parent set.
    """

    def __init__(self, command_sets: dict = None):
        self.root_set = None
        self.active_set = None
        self.command_sets = {}

        if command_sets is not None:
            self.setCommandSets(command_sets)
        else:
            # Example default command set if none is provided.
            self.setCommandSets(None)

    def setCommandSets(self, command_sets: (None, dict)):
        if command_sets is None:
            command_sets = {'name': '.', 'commands': {}}

        self.command_sets = command_sets
        if 'name' in self.command_sets:
            if self.root_set is None:
                self.root_set = self.command_sets['name']
                self.active_set = [self.command_sets['name']]
        else:
            raise ValueError("The command sets dictionary must have a 'name' key.")

    def parseCommand(self, command: str) -> dict:
        tokens = shlex.split(command)
        if not tokens:
            return {'success': False, 'error': 'Empty command'}

        # If the first token starts with a dot (and is not the parent token ".."), treat it as absolute.
        if tokens[0] != '..' and tokens[0].startswith('.'):
            if tokens[0] == '.':
                tokens.pop(0)
            else:
                tokens[0] = tokens[0][1:]
            start_path = [self.command_sets['name']]
            current_set = self.command_sets
        else:
            start_path = self.active_set.copy() if self.active_set else [self.command_sets['name']]
            current_set = self._get_set_by_path(start_path)

        new_path, cmd_name, remaining_tokens, nav_err = self._navigate(tokens, start_path, current_set)
        if nav_err:
            return {'success': False, 'error': nav_err}

        # If no command is specified then we are simply changing the active set.
        if cmd_name is None:
            self.active_set = new_path
            return {'success': True, 'type': 'change_set', 'active_set': new_path}

        target_set = self._get_set_by_path(new_path)
        if not target_set or 'commands' not in target_set or cmd_name not in target_set['commands']:
            return {'success': False, 'error': f"Command '{cmd_name}' not found in set {new_path}"}

        cmd_def = target_set['commands'][cmd_name]
        arg_defs = cmd_def.get('arguments', {})

        parsed_args, arg_err = self._parse_command_arguments(arg_defs, remaining_tokens)
        if arg_err:
            return {'success': False, 'error': arg_err}

        pos_args, kw_args = parsed_args

        # for arg_name, arg_def in arg_defs.items():
        #     key = arg_def.get('original_name') if arg_def.get('original_name') is not None else arg_name
        #     if arg_def.get('optional', False) or (arg_def.get('default') is not None):
        #         if key not in kw_args:
        #             kw_args[key] = arg_def.get('default')
        #     elif arg_def.get('is_flag', False):
        #         if key not in kw_args:
        #             kw_args[key] = False
        #     else:
        #         if key not in kw_args:
        #             return {'success': False, 'error': f"Argument '{arg_name}' was not provided"}

        result = {
            'success': True,
            'type': 'command',
            'command': {
                'name': cmd_name,
                'path': new_path,
                'arguments': {
                    'positional': pos_args,
                    'keyword': kw_args
                }
            },
            'active_set': self.active_set
        }
        return result

    def _get_set_by_path(self, path: list) -> dict:
        current = self.command_sets
        for p in path[1:]:
            if 'child_sets' in current and p in current['child_sets']:
                current = current['child_sets'][p]
            else:
                return None
        return current

    def _navigate(self, tokens: list, current_path: list, current_set: dict) -> (list, str, list, str):
        new_path = current_path.copy()
        i = 0
        # Process leading special tokens '.' and '..'
        while i < len(tokens):
            token = tokens[i]
            if token == '.':
                new_path = [self.command_sets['name']]
                current_set = self.command_sets
                i += 1
            elif token == '..':
                if len(new_path) > 1:
                    new_path.pop()
                    current_set = self._get_set_by_path(new_path)
                    i += 1
                else:
                    return new_path, None, tokens[i + 1:], "Already at root, cannot exit further."
            else:
                break

        # Process remaining tokens.
        while i < len(tokens):
            token = tokens[i]
            if token == '.':
                i += 1
                continue
            elif 'child_sets' in current_set and token in current_set['child_sets']:
                new_path.append(token)
                current_set = current_set['child_sets'][token]
                i += 1
            elif 'commands' in current_set and token in current_set['commands']:
                cmd_name = token
                i += 1
                return new_path, cmd_name, tokens[i:], None
            else:
                return new_path, None, tokens[i:], f"Token '{token}' not recognized in set {new_path}"
        return new_path, None, [], None

    def _parse_command_arguments(self, arg_defs: dict, tokens: list) -> ((list, dict), str):
        pos_args = []
        kw_args = {}
        i = 0

        def typecast_argument(arg_def: dict, val: str):
            mapping = {
                'int': int,
                'float': float,
                'bool': lambda x: x.lower() in ['true', '1', 'yes'] if isinstance(x, str) else bool(x),
                'str': str,
            }
            try:
                return mapping.get(arg_def.get("type", "str"), str)(val)
            except Exception:
                raise ValueError(f"Cannot convert value {val} to type {arg_def.get('type', 'str')}")

        while i < len(tokens):
            token = tokens[i]
            token = token.replace('–', '-').replace('−', '-')
            if token.startswith('--'):
                arg_name = token[2:]
                if arg_name not in arg_defs:
                    return None, f"Unknown argument: {arg_name}"
                arg_def = arg_defs[arg_name]
                key = arg_def.get('original_name') if arg_def.get('original_name') is not None else arg_name
                if arg_def.get('is_flag', False):
                    kw_args[key] = True
                    i += 1
                else:
                    if i + 1 >= len(tokens):
                        return None, f"Argument '{arg_name}' expects a value"
                    value_token = tokens[i + 1]
                    if arg_def.get('array_size', 0) > 0:
                        m = re.match(r'\[(.*)\]', value_token)
                        if not m:
                            return None, f"Argument '{arg_name}' expects a list enclosed in brackets."
                        values = [v.strip() for v in m.group(1).split(',')]
                        if len(values) != arg_def.get('array_size', 0):
                            return None, f"Argument '{arg_name}' expects a list of {arg_def.get('array_size', 0)} values."
                        try:
                            converted = [typecast_argument(arg_def, v) for v in values]
                        except Exception as e:
                            return None, str(e)
                        kw_args[key] = converted
                    else:
                        value_token = value_token.strip('"').strip("'")
                        try:
                            converted = typecast_argument(arg_def, value_token)
                        except Exception as e:
                            return None, str(e)
                        kw_args[key] = converted
                    i += 2
            elif token.startswith('-'):
                arg_short = token[1:]
                found = None
                for a_name, a_def in arg_defs.items():
                    if a_def.get('short_name') == arg_short:
                        found = a_name
                        break
                if not found:
                    return None, f"Unknown short argument: {arg_short}"
                arg_def = arg_defs[found]
                key = arg_def.get('original_name') if arg_def.get('original_name') is not None else found
                if arg_def.get('is_flag', False):
                    kw_args[key] = True
                    i += 1
                else:
                    if i + 1 >= len(tokens):
                        return None, f"Argument '{found}' expects a value"
                    value_token = tokens[i + 1]
                    if arg_def.get('array_size', 0) > 0:
                        m = re.match(r'\[(.*)\]', value_token)
                        if not m:
                            return None, f"Argument '{found}' expects a list enclosed in brackets."
                        values = [v.strip() for v in m.group(1).split(',')]
                        if len(values) != arg_def.get('array_size', 0):
                            return None, f"Argument '{found}' expects a list of {arg_def.get('array_size', 0)} values."
                        try:
                            converted = [typecast_argument(arg_def, v) for v in values]
                        except Exception as e:
                            return None, str(e)
                        kw_args[key] = converted
                    else:
                        value_token = value_token.strip('"').strip("'")
                        try:
                            converted = typecast_argument(arg_def, value_token)
                        except Exception as e:
                            return None, str(e)
                        kw_args[key] = converted
                    i += 2
            else:
                pos_args.append(token.strip('"').strip("'"))
                i += 1
        return (pos_args, kw_args), None
