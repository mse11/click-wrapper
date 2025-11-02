from typing import Dict, Union, List, Tuple, Any

from click_wrapper.importer import ClickImporter
from click.testing import CliRunner

class ClickInspector:

    def __init__(self, importer: ClickImporter):
        self._importer: ClickImporter = importer
        if not self._importer.py_import_path_attribute:
            raise ValueError("ClickImporter 'module_global_attribute' must be set ")
        self._metadata: List[Tuple[List,Any]] = self._metadata_generate()

    @property
    def script_string_import(self) -> str:
        return self._importer.build_import_line()

    @property
    def script_string_cli_obj(self) -> str:
        return str(self._importer.py_import_path_attribute)

    @property
    def script_string_package(self) -> str:
        return str(self._importer.py_import_package)

    @property
    def commands_names_as_lists(self) -> List[List[str]]:
        return self._metadata_commands_names(full_path=False, joined = False)

    @property
    def commands_names(self) -> List[str]:
        return self._metadata_commands_names(full_path=False, joined = True)

    @property
    def commands_names_full(self) -> List[str]:
        return self._metadata_commands_names(full_path=True, joined = True)

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
            result = CliRunner().invoke(self._importer.click_obj_cli_main, command + ["--help"])
            hyphenated = "-".join(command)
            if hyphenated:
                hyphenated = "-" + hyphenated
            output.append(f"\n(help{hyphenated})=")
            output.append("#" * heading_level + " llm " + " ".join(command) + " --help")
            output.append("```")
            output.append(result.output.replace("Usage: cli", "Usage: llm").strip())
            output.append("```")
        return "\n".join(output)

    @property
    def commands(self) -> Dict[str, Dict[str,Dict]]:
        return self._metadata_generate_as_dict()

    def _metadata_commands_names(self, full_path: bool = False, joined: bool = False) -> Union[List[str], List[List[str]]]:
        prefix = [self.script_string_package] if full_path else []

        commands_names = []
        for current_cmds_names, _ in self._metadata:
            # Remove first item of each list (it is e.g. 'cli')
            names = prefix + current_cmds_names[1:]
            commands_names.append(" ".join(names) if joined else names)
        return commands_names

    def _metadata_generate(self):
        """Traverse Click command tree and return metadata"""
        commands = []

        # Code inspired by Simon Willison
        #  - First find all commands and subcommands
        #  - List will be [ (["command"], click_object), (["command", "subcommand"], click_object) ...]

        def find_commands(command_obj, parent_cmds_names = None):
            parent_cmds_names  = parent_cmds_names or []
            current_cmds_names = parent_cmds_names + [command_obj.name]

            commands.append((current_cmds_names, command_obj))
            if hasattr(command_obj, "commands"):
                for subcommand in command_obj.commands.values():
                    find_commands(subcommand, current_cmds_names)

        find_commands(self._importer.click_obj_cli_main)

        return commands

    def _metadata_generate_as_dict(self) -> Dict[str, Dict[str,Dict]]:
        """Traverse Click command tree and return metadata."""
        data = {}
        for current_cmds_names, command_obj in self._metadata:
            cmd_path = " ".join(current_cmds_names[1:]) if len(current_cmds_names) > 1 else ""
            data[cmd_path or self.script_string_package] = ClickInspector._metadata_command_obj_as_dict(command_obj)
        return data

    @staticmethod
    def _metadata_command_obj_as_dict(command):
        """Extract metadata from a Click command, safely serialized."""
        meta = {
            "name": command.name,
            "help": command.help or "",
            "short_help": command.short_help or "",
            "params": [],
        }
        for param in command.params:
            param_info = {
                "name": param.name,
                "param_type_name": param.param_type_name,
                "opts": getattr(param, "opts", []),
                "secondary_opts": getattr(param, "secondary_opts", []),
                "required": getattr(param, "required", False),
                "default": ClickInspector._safe_serialize(getattr(param, "default", None)),
                "nargs": getattr(param, "nargs", 1),
                "multiple": getattr(param, "multiple", False),
                "help": getattr(param, "help", ""),
            }
            meta["params"].append(param_info)
        if hasattr(command, "commands"):
            meta["subcommands"] = {
                name: ClickInspector._metadata_command_obj_as_dict(subcmd)
                for name, subcmd in command.commands.items()
            }
        return meta

    @staticmethod
    def _safe_serialize(value):
        """Safely serialize Click objects and sentinels to JSON-friendly values."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple, set)):
            return [ClickInspector._safe_serialize(v) for v in value]
        if isinstance(value, dict):
            return {k: ClickInspector._safe_serialize(v) for k, v in value.items()}
        # Fallback: return string representation
        return str(value)