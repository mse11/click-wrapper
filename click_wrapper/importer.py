import importlib

from typing import Any

class ClickImporter:

    def __init__(self, module_import_path: str, module_global_attribute: str = None):
        """
        Dynamically import a module or attribute from a module using string paths.

        Args:
            module_import_path: Dot-separated module path (e.g., 'llm.cli')
            module_global_attribute: Optional attribute name to retrieve from the module
        """
        self.module_import_path: str = module_import_path
        self.module_global_attribute: str = module_global_attribute

        self.click_cli_main = ClickImporter.import_from_string(
            module_import_path,
            module_global_attribute
        )

    def build_import_line(self):
        return (
                f'from {self.module_import_path} import {self.module_global_attribute}'
                if self.module_global_attribute else
                f'import {self.module_import_path}'
        )

    @staticmethod
    def import_from_string(module_import_path: str, module_global_attribute: str = None) -> Any:
        """
        Dynamically import a module or attribute from a module using string paths.

        Args:
            module_import_path: Dot-separated module path (e.g., 'llm.cli')
            module_global_attribute: Optional attribute name to retrieve from the module

        Returns:
            The imported module, or the specified attribute if provided

        Raises:
            ImportError: If the module cannot be imported
            AttributeError: If the specified attribute doesn't exist in the module

        Examples:
            # Import entire module: equivalent to 'import llm.cli'
            module = import_from_string("llm.cli")

            # Import specific attribute: equivalent to 'from llm.cli import cli'
            cli = import_from_string("llm.cli", "cli")
        """
        ret_val = None
        try:
            ret_val = importlib.import_module(module_import_path)
        except ImportError as e:
            raise ImportError(
                f"Failed to import module '{module_import_path}': {e}"
            ) from e

        if module_global_attribute:
            try:
                ret_val = getattr(ret_val, module_global_attribute)
            except AttributeError as e:
                raise AttributeError(
                    f"Module '{module_import_path}' has no attribute '{module_global_attribute}'"
                ) from e

        return ret_val