from typing import Dict, Union, List, Tuple, Any, Optional
from click.testing import CliRunner

from click_wrapper import ClickImporter
from click_wrapper import ClickParser, ClickMetadata

class ClickGenerator:

    def __init__(self, importer: ClickImporter):
        self._parser = ClickParser.factory(importer)

    @property
    def commands_names_short(self):
        return self._parser.names_short

    @property
    def commands_names_short_joined(self):
        return self._parser.names_short_joined

    @property
    def commands_names_full_joined(self):
        return self._parser.names_full_joined

    @property
    def commands(self) -> Dict[str, ClickMetadata]:
        return self._parser.commands_map

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

