from typing import Dict, Union, List, Tuple, Any, Optional

from pathlib import Path

from click_wrapper import (
    ClickImporter,
    ClickParser,
    ClickWrapper,
)

class ClickGenerator:

    @staticmethod
    def app_help_dump(importer: ClickImporter) -> str:
        """
        Convenience function to generate help from a parser.

        Args:
            importer: ClickImporter instance

        Returns:
            Returns full help for Click command and its subcommands
        """
        parser = ClickParser.factory(importer)

        # Code inspired by Simon Willison
        # First find all commands and subcommands
        # List will be [["command"], ["command", "subcommand"], ...]
        # Remove first item of each list (it is 'cli')
        commands = parser.names_short
        # Now generate help for each one, with appropriate heading level
        output = []
        for command in commands:
            heading_level = len(command) + 2
            result = parser.importer.run_command(command + ["--help"])
            hyphenated = "-".join(command)
            if hyphenated:
                hyphenated = "-" + hyphenated
            output.append(f"\n(help{hyphenated})=")
            output.append("#" * heading_level + " llm " + " ".join(command) + " --help")
            output.append("```")
            output.append(result.replace("Usage: cli", "Usage: llm").strip())
            output.append("```")
        return "\n".join(output)

    @staticmethod
    def app_wrapper(importer: ClickImporter, output_file: str = None) -> str:
        """
        Convenience function to generate wrapper code from a parser.

        Args:
            importer: ClickImporter instance
            output_file: file path

        Returns:
            Complete generated Python code as string
        """
        generator = ClickWrapper(importer)
        code_string = generator.generate()

        if output_file:
            Path(output_file).write_text(code_string)

        return code_string
