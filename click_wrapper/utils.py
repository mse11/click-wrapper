from click import Command
from typing import Dict, List, Union
from types import ModuleType

from click_wrapper import (
    ClickImporter,
    ClickParser,
    ClickMetadata,
    ClickGenerator,
    ClickWrapper,
)

class ClickUtils:

    @staticmethod
    def import_from_string(py_import_path: str, py_import_path_attribute: str = None) -> Union[ModuleType, Command]:
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
    def commands_metadata(module_import_path: str, module_global_attribute: str) -> Dict[str, ClickMetadata]:
        importer = ClickImporter(
            py_import_path=module_import_path,
            py_import_path_attribute=module_global_attribute,
        )
        return ClickGenerator(importer).commands_map

    @staticmethod
    def dump_help(module_import_path: str, module_global_attribute: str) -> str:
        importer = ClickImporter(
            py_import_path=module_import_path,
            py_import_path_attribute=module_global_attribute,
        )
        return ClickGenerator(importer).commands_help_dump

    @staticmethod
    def dump_wrapper(module_import_path: str, module_global_attribute: str):
        # Example: Generate wrapper for 'llm' CLI tool
        importer = ClickImporter(
            py_import_path=module_import_path,
            py_import_path_attribute=module_global_attribute,
        )
        parser = ClickParser.factory(importer)

        generated_code = ClickWrapper.generate_wrapper_code(parser)
        return generated_code