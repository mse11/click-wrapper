from typing import Dict, Union, List, Tuple, Any, Optional
from dataclasses import dataclass, field, asdict

from click_wrapper.importer import ClickImporter

################################################################################################################

@dataclass
class ClickParamData:
    """Information about a Click command parameter."""
    name: str
    param_type_name: str
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
    def to_dict(self) -> dict:
        return asdict(self)

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

    def to_dict(self) -> dict:
        return asdict(self)

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
    def script_string_import(self) -> str:
        return self.importer.build_import_line()

    @property
    def script_string_cli_obj(self) -> str:
        return str(self.importer.py_import_path_attribute)

    @property
    def script_string_package(self) -> str:
        return str(self.importer.py_import_package)

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

    ##############
    # internal
    ##############
    def _commands_map(self, full_dict: bool = False) -> Union[Dict[str, ClickMetadata], Dict[str, Dict[str,Dict]]]:
        data = {}
        for m in self.metadata:
            cmd_path = m.name_short_joined or self.importer.py_import_package
            data[cmd_path] = m.cmd_data.to_dict() if full_dict else m.cmd_data
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

        def find_commands(command_obj, parent_cmds_names = None):
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
    def _click_parse_command_obj(command) -> ClickCommandData:
        """Extract metadata from a Click command as a CommandMetadata dataclass."""

        # Extract parameters
        params = []
        dbg_params = []
        for param in command.params:
            param_info = ClickParser._click_parse_param_obj(param)
            params.append(param_info)
            dbg_params.append(param.name)

        # Extract subcommands
        subcommands = {}
        dbg_subcommands = []
        if hasattr(command, "commands"):
            subcommands = {
                name: ClickParser._click_parse_command_obj(subcmd)
                for name, subcmd in command.commands.items()
            }
            dbg_subcommands = list(command.commands.keys())

        return ClickCommandData(
            fnc_name=command.name,
            default_cmd_name=getattr(command, "default_cmd_name", None),
            default_if_no_args=getattr(command, "default_if_no_args", None),
            fnc_dbg_params=dbg_params,
            fnc_dbg_subcommands=dbg_subcommands,
            fnc_help_short=command.short_help or "",
            fnc_help=command.help or "",
            fnc_params=params,
            fnc_subcommands=subcommands,
        )

    @staticmethod
    def _click_parse_param_obj(param) -> ClickParamData:
        """Extract parameter information into a ParamInfo dataclass."""
        return ClickParamData(
            name=param.name,
            param_type_name=param.param_type_name,
            opts=getattr(param, "opts", []),
            secondary_opts=getattr(param, "secondary_opts", []),
            required=getattr(param, "required", False),
            default=ClickParser._safe_serialize(getattr(param, "default", None)),
            nargs=getattr(param, "nargs", 1),
            multiple=getattr(param, "multiple", False),
            help=getattr(param, "help", ""),
            envvar=param.envvar,
        )

    @staticmethod
    def _safe_serialize(value):
        """Safely serialize Click objects and sentinels to JSON-friendly values."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple, set)):
            return [ClickParser._safe_serialize(v) for v in value]
        if isinstance(value, dict):
            return {k: ClickParser._safe_serialize(v) for k, v in value.items()}
        # Fallback: return string representation
        return str(value)
