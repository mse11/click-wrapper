from typing import Dict, Union, List, Tuple, Any, Optional
from click import Command
from click.testing import CliRunner

class ClickRunnerError(Exception):
    """Exception raised when cli command fails"""
    pass

class ClickRunner:
    """
    Wrapper for Click CLI operations using Click's CliRunner.

    This wrapper provides a Pythonic interface to the Click command-line tool,
    allowing you to execute CLI commands programmatically without subprocess overhead.
    """

    def __init__(self, cli_main_function: Command, cmd_base: str):
        """
        Initialize the ClickRunner wrapper.

        Args:
            cli_main_function: The main CLI function object (e.g., from llm.cli import cli)
            cmd_base: CLI tool name (e.g., llm)
        """
        self.runner = CliRunner()
        self.cli_main_obj = cli_main_function
        self.cli_base = cmd_base

    def run_command(self, args: List[str], input: Optional[str] = None) -> str:
        """
        Run a CLI command and return the result.

        Args:
            args: List of command arguments
            input: Optional stdin input

        Returns:
            Result output (stripped of trailing whitespace)

        Raises:
            ClickRunnerError: If command fails (non-zero exit code)
        """
        result = self.runner.invoke(self.cli_main_obj, args, input=input)

        if result.exit_code != 0:
            full_cmd = [self.cli_base] + args + ([input] if input else [])
            raise ClickRunnerError(f"""Command {' '.join(full_cmd)} failed: {result.output}""")

        return result.output