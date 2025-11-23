import importlib
from typing import Union, List, Optional
from types import ModuleType
from click import Command
from click.testing import CliRunner

class ClickImporterError(Exception):
    """Exception raised when cli command fails"""
    pass

class ClickImporter:

    def __init__(self, py_import_path: str, py_import_path_attribute: str = None):
        """
        Wrapper for Click CLI operations using Click's CliRunner.

        This wrapper provides a Pythonic interface to the Click command-line tool,
        allowing you to execute CLI commands programmatically without subprocess overhead.

        Dynamically import a module and attribute from a module using string paths.
        When py_import_path_attribute is None and a simple module name is provided
        (no dots in path), automatically attempts to import 'cli' attribute from
        '__main__.py' of that package.

        Args:
            py_import_path: Dot-separated python module path (e.g., 'llm.cli').
                If a simple name is provided without py_import_path_attribute (e.g., 'llm'),
                automatically expands to 'llm.__main__' with attribute 'cli'.
            py_import_path_attribute: Optional attribute name to retrieve from the
                'py_import_path' module. When None and py_import_path is a simple
                module name, defaults to 'cli' from '__main__' module.

        Examples:
            >>> # Explicit import path
            >>> importer = ClickImporter('llm.cli', 'main')

            >>> # Auto-detection for standard Click CLI program structure
            >>> # Assumes package structure with __main__.py:
            >>> #   from .cli import cli
            >>> #   if __name__ == "__main__":
            >>> #       cli()
            >>> importer = ClickImporter('llm')  # Expands to 'llm.__main__' with 'cli'

        Raises:
            ImportError: If the module cannot be imported
            AttributeError: If the specified attribute doesn't exist in the module
        """
        # check if user expect simple structure of Click CLI application
        if (not py_import_path_attribute) and len(py_import_path.split('.')) == 1:
            py_import_path           = py_import_path + ".__main__"
            py_import_path_attribute = "cli"

        self.py_import_path: str = py_import_path
        self.py_import_path_attribute: str = py_import_path_attribute
        self.py_import_package: str = py_import_path.split(".")[0]

        self.runner = CliRunner()
        self.click_obj_cli_main: Union[ModuleType, Command] = self._import_from_string()

    def run_command(self, args: List[str], input: Optional[str] = None) -> str:
        """
        Run a CLI command and return the result.

        Args:
            args: List of command arguments
            input: Optional stdin input

        Returns:
            Result output (stripped of trailing whitespace)

        Raises:
            ClickImporterError: If command fails (non-zero exit code)
        """
        result = self.runner.invoke(self.click_obj_cli_main, args, input=input)

        if result.exit_code != 0:
            full_cmd = [self.py_import_package] + args + ([input] if input else [])
            raise ClickImporterError(f"""Command {' '.join(full_cmd)} failed: {result.output}""")

        return result.output

    def _import_from_string(self) -> Union[ModuleType, Command]:

        ret_val = None
        try:
            ret_val = importlib.import_module(self.py_import_path)
        except ImportError as e:
            raise ImportError(
                f"Failed to import module '{self.py_import_path}': {e}"
            ) from e

        if self.py_import_path_attribute:
            try:
                ret_val = getattr(ret_val, self.py_import_path_attribute)
            except AttributeError as e:
                raise AttributeError(
                    f"Module '{self.py_import_path}' has no attribute '{self.py_import_path_attribute}'"
                ) from e

        return ret_val