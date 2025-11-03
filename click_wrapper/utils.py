
from click_wrapper import ClickImporter
from click_wrapper import ClickGenerator

from typing import Any, Dict, List

class ClickUtils:

    @staticmethod
    def import_from_string(py_import_path: str, py_import_path_attribute: str = None) -> Any:
        """
        Dynamically import a module or attribute from a module using string paths.

        Args:
            py_import_path: Dot-separated module path (e.g., 'llm.cli')
            py_import_path_attribute: Optional attribute name to retrieve from the 'py_import_path' module

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
        importer = ClickImporter(
            py_import_path=py_import_path,
            py_import_path_attribute=py_import_path_attribute,
        )
        return importer.click_obj_cli_main

    @staticmethod
    def commands_names(
            module_import_path: str,
            module_global_attribute: str,
            full_path: bool
    ) -> List[str]:
        importer = ClickImporter(
            py_import_path=module_import_path,
            py_import_path_attribute=module_global_attribute,
        )
        if full_path:
            return ClickGenerator(importer).commands_names_full_joined
        else:
            return ClickGenerator(importer).commands_names_short_joined

    @staticmethod
    def help_dump(module_import_path: str, module_global_attribute: str) -> str:
        importer = ClickImporter(
            py_import_path=module_import_path,
            py_import_path_attribute=module_global_attribute,
        )
        return ClickGenerator(importer).commands_help_dump

    @staticmethod
    def parse_cli_metadata(module_import_path: str, module_global_attribute: str) -> Dict[str, Dict[str,Dict]]:
        importer = ClickImporter(
            py_import_path=module_import_path,
            py_import_path_attribute=module_global_attribute,
        )
        return ClickGenerator(importer).commands
