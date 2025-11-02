
from click_wrapper.importer import ClickImporter
from click_wrapper.inspector import ClickInspector
from click_wrapper.generator import ClickWrapperGenerator

from typing import Any, Optional, Dict

class ClickUtils:

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
        importer = ClickImporter(
            module_import_path=module_import_path,
            module_global_attribute=module_global_attribute,
        )
        return importer.click_cli_main

    @staticmethod
    def help_dump(module_import_path: str, module_global_attribute: str) -> str:
        importer = ClickImporter(
            module_import_path=module_import_path,
            module_global_attribute=module_global_attribute,
        )
        return ClickInspector(importer).generate_help_dump()

    @staticmethod
    def parse_cli_metadata(module_import_path: str, module_global_attribute: str) -> Dict:
        importer = ClickImporter(
            module_import_path=module_import_path,
            module_global_attribute=module_global_attribute,
        )
        return ClickInspector(importer).generate_metadata()

    @staticmethod
    def generate_wrapper_from_cli(module_import_path: str,
                                  module_global_attribute: str,
                                  wrapper_class_name: str = "ClickWrapper",
                                  output_file: Optional[str] = None) -> str:

        # Extract metadata from cli object
        importer = ClickImporter(
            module_import_path=module_import_path,
            module_global_attribute=module_global_attribute,
        )
        inspector = ClickInspector(importer)

        # Generate wrapper
        generator = ClickWrapperGenerator(inspector, wrapper_class_name=wrapper_class_name)
        code = generator.generate_wrapper_class()

        # Optionally write to file
        if output_file:
            with open(output_file, 'w') as f:
                f.write(code)
            print(f"Wrapper generated: {output_file}")

        return code