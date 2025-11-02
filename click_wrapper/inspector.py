from typing import Dict, Union, List, Tuple, Any, Optional
from dataclasses import dataclass, field, asdict

from click_wrapper.importer import ClickImporter
from click.testing import CliRunner

@dataclass
class ParamInfo:
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


@dataclass
class CommandMetadata:
    """Metadata for a Click command."""
    fnc_name: str
    default_cmd_name: Optional[str] = None
    default_if_no_args: Optional[bool] = None
    fnc_dbg_params: list[str] = field(default_factory=list)
    fnc_dbg_subcommands: list[str] = field(default_factory=list)
    fnc_help_short: str = ""
    fnc_help: str = ""
    fnc_params: list[ParamInfo] = field(default_factory=list)
    fnc_subcommands: dict[str, 'CommandMetadata'] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

@dataclass
class CommandPath:
    """Represents a command with its full path in the command tree."""
    path: list[str]
    metadata: CommandMetadata

@dataclass
class CommandPaths:
    importer: ClickImporter
    paths: List[CommandPath] = field(default_factory=list)

    def to_dict(self, full_dict: bool = False) -> Dict[str, Dict[str,Dict]]:
        data = {}
        for p in self.paths:
            cmd_path = " ".join(p.path[1:]) if len(p.path) > 1 else ""
            data[cmd_path or self.importer.py_import_package] = p.metadata.to_dict() if full_dict else p.metadata
        return data

    def commands_names(self, full_path: bool = False, joined: bool = False) -> Union[List[str], List[List[str]]]:
        prefix = [self.script_string_package] if full_path else []

        commands_names = []
        for p in self.paths:
            # Remove first item of each list (it is e.g. 'cli')
            names = prefix + p.path[1:]
            commands_names.append(" ".join(names) if joined else names)
        return commands_names

    @property
    def script_string_import(self) -> str:
        return self.importer.build_import_line()

    @property
    def script_string_cli_obj(self) -> str:
        return str(self.importer.py_import_path_attribute)

    @property
    def script_string_package(self) -> str:
        return str(self.importer.py_import_package)

    @staticmethod
    def click_parse(importer: ClickImporter) -> 'CommandPaths':
        """Traverse Click command tree and return metadata"""
        commands = CommandPaths(importer)

        # Code inspired by Simon Willison
        #  - First find all commands and subcommands
        #  - List will be [ (["command"], click_object), (["command", "subcommand"], click_object) ...]

        def find_commands(command_obj, parent_cmds_names = None):
            parent_cmds_names  = parent_cmds_names or []
            current_cmds_names = parent_cmds_names + [command_obj.name]

            cmd_path_obj = CommandPath(
                path=current_cmds_names,
                metadata=CommandPaths._click_parse_command_obj(command_obj)
            )

            commands.paths.append(cmd_path_obj)
            if hasattr(command_obj, "commands"):
                for subcommand in command_obj.commands.values():
                    find_commands(subcommand, current_cmds_names)

        find_commands(importer.click_obj_cli_main)

        return commands

    @staticmethod
    def _click_parse_command_obj(command) -> CommandMetadata:
        """Extract metadata from a Click command as a CommandMetadata dataclass."""

        # Extract parameters
        params = []
        dbg_params = []
        for param in command.params:
            param_info = CommandPaths._click_parse_param_obj(param)
            params.append(param_info)
            dbg_params.append(param.name)

        # Extract subcommands
        subcommands = {}
        dbg_subcommands = []
        if hasattr(command, "commands"):
            subcommands = {
                name: CommandPaths._click_parse_command_obj(subcmd)
                for name, subcmd in command.commands.items()
            }
            dbg_subcommands = list(command.commands.keys())

        return CommandMetadata(
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
    def _click_parse_param_obj(param) -> ParamInfo:
        """Extract parameter information into a ParamInfo dataclass."""
        return ParamInfo(
            name=param.name,
            param_type_name=param.param_type_name,
            opts=getattr(param, "opts", []),
            secondary_opts=getattr(param, "secondary_opts", []),
            required=getattr(param, "required", False),
            default=CommandPaths._safe_serialize(getattr(param, "default", None)),
            nargs=getattr(param, "nargs", 1),
            multiple=getattr(param, "multiple", False),
            help=getattr(param, "help", ""),
        )

    @staticmethod
    def _safe_serialize(value):
        """Safely serialize Click objects and sentinels to JSON-friendly values."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple, set)):
            return [CommandPaths._safe_serialize(v) for v in value]
        if isinstance(value, dict):
            return {k: CommandPaths._safe_serialize(v) for k, v in value.items()}
        # Fallback: return string representation
        return str(value)


########################################################

class ClickInspector:

    def __init__(self, importer: ClickImporter):

        if not importer.py_import_path_attribute:
            raise ValueError("ClickImporter 'module_global_attribute' must be set ")

        self._metadata = CommandPaths.click_parse(importer)

    @property
    def commands_names_as_lists(self) -> List[List[str]]:
        return self._metadata.commands_names(full_path=False, joined = False)

    @property
    def commands_names(self) -> List[str]:
        return self._metadata.commands_names(full_path=False, joined = True)

    @property
    def commands_names_full(self) -> List[str]:
        return self._metadata.commands_names(full_path=True, joined = True)

    @property
    def commands(self) -> Dict[str, Dict[str,Dict]]:
        return self._metadata.to_dict()

    @property
    def commands_help_dump(self) -> str:
        """Return full help for Click command and its subcommands (Simon Willison format)"""

        # First find all commands and subcommands
        # List will be [["command"], ["command", "subcommand"], ...]
        # Remove first item of each list (it is 'cli')
        commands = self.commands_names_as_lists
        # Now generate help for each one, with appropriate heading level
        output = []
        for command in commands:
            heading_level = len(command) + 2
            result = CliRunner().invoke(self._metadata.importer.click_obj_cli_main, command + ["--help"])
            hyphenated = "-".join(command)
            if hyphenated:
                hyphenated = "-" + hyphenated
            output.append(f"\n(help{hyphenated})=")
            output.append("#" * heading_level + " llm " + " ".join(command) + " --help")
            output.append("```")
            output.append(result.output.replace("Usage: cli", "Usage: llm").strip())
            output.append("```")
        return "\n".join(output)





