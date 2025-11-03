from typing import Dict, Union, List, Tuple, Any, Optional
from click.testing import CliRunner

from click_wrapper import ClickImporter
from click_wrapper import ClickParser

class ClickGenerator:

    def __init__(self, importer: ClickImporter):

        if not importer.py_import_path_attribute:
            raise ValueError("ClickImporter 'module_global_attribute' must be set ")

        self._parser = ClickParser.click_parse(importer)

    @property
    def commands_names_short(self):
        return [m.name_short for m in self._parser.metadata]

    @property
    def commands_names_short_joined(self):
        return [m.name_short_joined for m in self._parser.metadata]

    @property
    def commands_names_full_joined(self):
        return [m.name_full_joined for m in self._parser.metadata]

    @property
    def commands(self) -> Dict[str, Dict[str,Dict]]:
        return self._parser.to_dict()

    @property
    def commands_help_dump(self) -> str:
        """Return full help for Click command and its subcommands"""

        # Code inspired by Simon Willison
        # First find all commands and subcommands
        # List will be [["command"], ["command", "subcommand"], ...]
        # Remove first item of each list (it is 'cli')
        commands = self.commands_names_short
        # Now generate help for each one, with appropriate heading level
        output = []
        for command in commands:
            heading_level = len(command) + 2
            result = CliRunner().invoke(self._parser.importer.click_obj_cli_main, command + ["--help"])
            hyphenated = "-".join(command)
            if hyphenated:
                hyphenated = "-" + hyphenated
            output.append(f"\n(help{hyphenated})=")
            output.append("#" * heading_level + " llm " + " ".join(command) + " --help")
            output.append("```")
            output.append(result.output.replace("Usage: cli", "Usage: llm").strip())
            output.append("```")
        return "\n".join(output)

