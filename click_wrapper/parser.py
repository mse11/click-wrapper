import pathlib
import uuid

from click import Command
from click import types
from click.core import UNSET

from typing import Dict, Union, List, Tuple, Any, Type, Optional
from dataclasses import dataclass, field, asdict

from click_wrapper.importer import ClickImporter

class ClickHelper:

    type_mapping: dict[Type[types.ParamType], Type] = {
        types.StringParamType: str,
        types.IntParamType: int,
        types.FloatParamType: float,
        types.BoolParamType: bool,
        types.UUIDParameterType: str,  # uuid.UUID
        types.File: Any,  # File objects
        types.Path: str,  # pathlib.Path
        types.Choice: str,
        types.IntRange: int,
        types.FloatRange: float,
        types.DateTime: str,  # or datetime.datetime
        types.Tuple: tuple
    }

    @staticmethod
    def to_help_string_lines(
            help_msg,
            indent: str,
            dump_empty: bool = False,
            use_borders: bool = True
    ) -> List[str]:
        lines = []
        if help_msg or dump_empty:
            if use_borders:
                lines.append(f'{indent}"""')
            for l in help_msg.split('\n'):
                lines.append(f"{indent}{l}")
            if use_borders:
                lines.append(f'{indent}"""')
        return lines

    @staticmethod
    def sanitize_help_string(help_str, prefix: str = "", suffix: str = ""):
        if isinstance(help_str, str):
            #git gui
            help_str = help_str.replace('\b', '')
            help_str =  "\n".join([ l for l in help_str.split("\n") if l.strip()])
            help_str = prefix + help_str + suffix
        return help_str

    @staticmethod
    def click_type_to_python_type_as_string(
            click_param_type: types.ParamType,
            default_type_class: Type
    ) -> str:
        """Get the string representation of the base Python type."""

        python_type: Type = ClickHelper.click_type_to_python_type(click_param_type, default_type_class)
        # Convert Type to string representation
        if hasattr(python_type, '__name__'):
            return python_type.__name__

        return str(python_type)

    @staticmethod
    def click_type_to_python_type(
            click_param_type: types.ParamType,
            default_type_class: Type
    ) -> Type:
        py_type: Type = default_type_class
        if ClickHelper.is_click_type(click_param_type):
            py_type = ClickHelper.type_mapping[type(click_param_type)]
        else:
            print(f"{str(click_param_type)} not in type mapping dictionary")
        return py_type

    @staticmethod
    def is_click_type(click_param_type: types.ParamType) -> bool:
        return type(click_param_type) in ClickHelper.type_mapping

################################################################################################################

@dataclass
class ClickParamData:
    """Information about a Click command parameter."""
    name: str
    param_type_click: types.ParamType
    param_type_name: str
    param_type_is_argument: bool
    param_type_is_option: bool
    is_flag: bool
    opts: list[str] = field(default_factory=list)
    secondary_opts: list[str] = field(default_factory=list)
    required: bool = False
    default: Any = None
    nargs: int = 1
    multiple: bool = False
    help: str = ""
    envvar: Union[str, None] = None

    ##############
    # api extra
    ##############
    def is_mandatory_python(self):
        return self.required #or self.param_type_is_argument

    def to_dict(self) -> dict:
        return asdict(self)

    def to_help_string_lines(self, indent: str , dump_empty: bool = False) -> List[str]:
        return ClickHelper.to_help_string_lines(
            f"{self.help}. Environment variable '{self.envvar}'" if self.envvar else self.help,
            indent,
            dump_empty=dump_empty
        )

    def as_string_python_type(self) -> str:
        """Determine Python type annotation string from Click parameter."""

        # Get base type using the mapping
        base_type = ClickHelper.click_type_to_python_type_as_string(self.param_type_click, str)

        # Handle multiple values
        if self.multiple or self.nargs > 1 or self.nargs == -1:
            if isinstance(self.param_type_click, types.Tuple):
                # Get tuple element types as strings
                element_types = ', '.join(
                    ClickHelper.click_type_to_python_type_as_string(t, str) for t in self.param_type_click.types
                )
                base_type = f"List[Tuple[{element_types}]]"
            else:
                base_type = f"List[{base_type}]"

        # Make optional if not required
        if not self.is_mandatory_python():
            base_type = f"Optional[{base_type}]"

        return base_type

    def as_string_default_value(self) -> str:
        """Get default value for field."""
        if self.multiple or self.nargs > 1 or self.nargs == -1:
            return "None"

        if self.default is not None and self.default != "":
            if isinstance(self.default, bool):
                return str(self.default)
            elif isinstance(self.default, (int, float)):
                return str(self.default)
            elif isinstance(self.default, str):
                return f'"{self.default}"'
            else:
                return "None"

        # For flags/boolean options
        if self.param_type_name.lower() == "boolean":
            return "False"

        return "None"

################################################################################################################

@dataclass
class ClickCommandData:
    """Metadata for a Click command."""
    fnc_name: str
    default_cmd_name: Optional[str] = None
    default_if_no_args: Optional[bool] = None
    fnc_dbg_params: list[str] = field(default_factory=list)
    fnc_dbg_subcommands: list[str] = field(default_factory=list)
    fnc_help_short: str = ""
    fnc_help: str = ""
    fnc_params: list[ClickParamData] = field(default_factory=list)
    fnc_subcommands: dict[str, 'ClickCommandData'] = field(default_factory=dict)

    ##############
    # api extra
    ##############
    @property
    def is_leaf(self):
        return False if len(self.fnc_subcommands) else True

    @property
    def has_mandatory(self):
        return True if len(self.params_mandatory) > 0 else False

    @property
    def params_mandatory(self):
        return [p for p in self.fnc_params if p.is_mandatory_python()]

    @property
    def params_optional(self):
        return [p for p in self.fnc_params if not p.is_mandatory_python()]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_help_string_lines(
            self,
            indent: str,
            no_help_msg: str = None,
            dump_empty: bool = False,
            use_borders: bool = True
    ) -> List[str]:
        return ClickHelper.to_help_string_lines(
            help_msg=self.fnc_help or self.fnc_help_short or no_help_msg,
            indent=indent,
            dump_empty=dump_empty,
            use_borders=use_borders
        )

################################################################################################################

@dataclass
class ClickMetadata:
    cmd_base: str
    cmd_path: list[str]
    cmd_data: ClickCommandData

    ##############
    # api extra
    ##############

    @property
    def name_short(self) -> List[List[str]]:
        return self._name(full_path=False, joined = False)
    @property
    def name_short_joined(self) -> List[str]:
        return self._name(full_path=False, joined = True)
    @property
    def name_full(self) -> List[str]:
        return self._name(full_path=True, joined = False)
    @property
    def name_full_joined(self) -> List[str]:
        return self._name(full_path=True, joined = True)
    @property
    def is_leaf(self):
        return self.cmd_data.is_leaf

    def to_dict(self) -> dict:
        return asdict(self)

    ##############
    # internal
    ##############
    def _name(self, full_path: bool = False, joined: bool = False) -> Union[List[str], List[List[str]]]:
        prefix = [self.cmd_base] if full_path else []
        # Remove first item of each list (it is e.g. 'cli')
        name = prefix + self.cmd_path[1:]
        return " ".join(name) if joined else name


################################################################################################################

@dataclass
class ClickParser:
    importer: ClickImporter
    metadata: List[ClickMetadata] = field(default_factory=list)

    def __post_init__(self):
        if not self.importer.py_import_path_attribute:
            raise ValueError("ClickImporter 'module_global_attribute' must be set ")

    ##############
    # api extra
    ##############
    @property
    def script_string_import_path(self) -> str:
        return self.importer.py_import_path

    @property
    def script_string_import_attribute(self) -> str:
        return self.importer.py_import_path_attribute

    @property
    def script_string_package(self) -> str:
        return self.importer.py_import_package

    @property
    def names_short(self):
        return [m.name_short for m in self.metadata]

    @property
    def names_short_joined(self):
        return [m.name_short_joined for m in self.metadata]

    @property
    def names_full_joined(self):
        return [m.name_full_joined for m in self.metadata]

    @property
    def commands_map(self) -> Dict[str, ClickMetadata]:
        return self._commands_map(full_dict=False)

    @property
    def commands_as_dict(self) -> Dict[str, Dict[str,Dict]]:
        return self._commands_map(full_dict=True)

    ##############
    # internal
    ##############
    def _commands_map(self, full_dict: bool = False) -> Union[Dict[str, ClickMetadata], Dict[str, Dict[str,Dict]]]:
        data = {}
        for m in self.metadata:
            cmd_path = m.name_short_joined or self.importer.py_import_package
            data[cmd_path] = m.to_dict() if full_dict else m
        return data

    ##############
    # parsing
    ##############
    @staticmethod
    def factory(importer: ClickImporter) -> 'ClickParser':
        """Traverse Click command tree and return metadata"""
        parser = ClickParser(importer)

        # Code inspired by Simon Willison
        #  - First find all commands and subcommands
        #  - List will be [ (["command"], click_object), (["command", "subcommand"], click_object) ...]

        def find_commands(command_obj: Command, parent_cmds_names = None):
            parent_cmds_names  = parent_cmds_names or []
            current_cmds_names = parent_cmds_names + [command_obj.name]

            cmd_path_obj = ClickMetadata(
                cmd_base=parser.script_string_package,
                cmd_path=current_cmds_names,
                cmd_data=ClickParser._click_parse_command_obj(command_obj)
            )

            parser.metadata.append(cmd_path_obj)
            if hasattr(command_obj, "commands"):
                for subcommand in command_obj.commands.values():
                    find_commands(subcommand, current_cmds_names)

        find_commands(importer.click_obj_cli_main)

        return parser

    @staticmethod
    def _click_parse_command_obj(click_command_obj) -> ClickCommandData:
        """Extract metadata from a Click command as a CommandMetadata dataclass."""

        # Extract parameters
        params = []
        dbg_params = []
        for param in click_command_obj.params:
            param_info = ClickParser._click_parse_param_obj(param)
            # if 'attachment_types' == param_info.name:
            #     print(param_info.help)
            params.append(param_info)
            dbg_params.append(param.name)

        # Extract subcommands
        subcommands = {}
        dbg_subcommands = []
        if hasattr(click_command_obj, "commands"):
            subcommands = {
                name: ClickParser._click_parse_command_obj(subcmd)
                for name, subcmd in click_command_obj.commands.items()
            }
            dbg_subcommands = list(click_command_obj.commands.keys())

        return ClickCommandData(
            fnc_name=click_command_obj.name,
            default_cmd_name=getattr(click_command_obj, "default_cmd_name", None),
            default_if_no_args=getattr(click_command_obj, "default_if_no_args", None),
            fnc_dbg_params=dbg_params,
            fnc_dbg_subcommands=dbg_subcommands,
            fnc_help_short=click_command_obj.short_help or "",
            fnc_help=ClickHelper.sanitize_help_string(click_command_obj.help or ""),
            fnc_params=params,
            fnc_subcommands=subcommands,
        )

    @staticmethod
    def _click_parse_param_obj(click_param_obj) -> ClickParamData:
        """Extract parameter information into a ParamInfo dataclass."""
        return ClickParamData(
            name=click_param_obj.name,
            param_type_click=click_param_obj.type,
            param_type_name=click_param_obj.param_type_name,
            param_type_is_argument=click_param_obj.param_type_name == 'argument',
            param_type_is_option=click_param_obj.param_type_name == 'option',
            is_flag=getattr(click_param_obj, "is_flag", False),
            opts=getattr(click_param_obj, "opts", []),
            secondary_opts=getattr(click_param_obj, "secondary_opts", []),
            required=getattr(click_param_obj, "required", False),
            default=ClickParser._safe_serialize(getattr(click_param_obj, "default", None)),
            nargs=getattr(click_param_obj, "nargs", 1),
            multiple=getattr(click_param_obj, "multiple", False),
            help=ClickHelper.sanitize_help_string(
                help_str=getattr(click_param_obj, "help", ""),
                prefix=f"""{click_param_obj.param_type_name}{"_flag" if getattr(click_param_obj, "is_flag", False) else ""}: """
            ),
            envvar=click_param_obj.envvar,
        )

    @staticmethod
    def _safe_serialize(value):
        """Safely serialize Click objects and sentinels to JSON-friendly values."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if value is UNSET:
            return None
        if isinstance(value, (list, tuple, set)):
            return [ClickParser._safe_serialize(v) for v in value]
        if isinstance(value, dict):
            return {k: ClickParser._safe_serialize(v) for k, v in value.items()}
        # Fallback: return string representation
        return str(value)
