from typing import Dict, Union, List, Tuple, Any, Optional
import inspect
from pathlib import Path

from click_wrapper import (
    ClickDataCommand,
    ClickParser,
    ClickImporter,
    ClickDataParam,
)

class ClickWrapper:
    """Generates wrapper code for Click CLI commands."""

    def __init__(self, importer: ClickImporter):
        self.parser = ClickParser.factory(importer)
        self.indent = "    "

    ##############
    # api extra
    ##############

    @staticmethod
    def generate_wrapper_code(importer: ClickImporter, output_file: str = None) -> str:
        """
        Convenience function to generate wrapper code from a parser.

        Args:
            importer: ClickImporter instance

        Returns:
            Complete generated Python code as string
        """
        generator = ClickWrapper(importer)
        code_string =  generator.generate()

        if output_file:
            Path(output_file).write_text(code_string)

        return code_string

    def generate(self) -> str:
        """Generate complete wrapper code including imports, dataclasses, and methods."""
        parts = [
            self._generate_imports(),
            self._generate_base_class(),
            self._generate_dataclasses(),
            self._generate_wrapper_class(),
        ]
        return "\n\n".join(parts)

    ##############
    # internal imports
    ##############
    def _generate_imports(self) -> str:
        """Generate import statements."""
        return '\n'.join([
            "from typing import Tuple",
            "from dataclasses import dataclass"
        ])

    ##############
    # internal base class (importer + runner)
    ##############
    def _generate_base_class(self) -> str:
        """Generate base exception class."""
        module = inspect.getmodule(ClickImporter)
        source = inspect.getsource(module)
        return source.replace(ClickImporter.__name__, self._get_class_base_name())

    ##############
    # internal dataclass (input parameters)
    ##############
    def _generate_dataclasses(self) -> str:
        """Generate dataclasses for all leaf commands."""
        dataclasses = []
        for name, metadata in self.parser.commands_map.items():
            if metadata.is_leaf:
                dataclass_code = self._generate_dataclass(name, metadata.cmd_data)
                dataclasses.append(dataclass_code)
        return "\n\n".join(dataclasses)

    def _generate_dataclass(self, cmd_name: str, cmd_data: ClickDataCommand) -> str:
        """Generate a dataclass for a specific command."""
        lines = [
            "@dataclass",
            f"class {self._get_dataclass_name(cmd_name)}:",
            *cmd_data.to_help_string_lines(indent=self.indent, no_help_msg=f"Options for '{cmd_name}' command")
        ]

        # Generate fields
        if not cmd_data.fnc_params:
            lines.append(f"{self.indent}pass")
        else:
            for param in cmd_data.fnc_params:
                field_lines = self._generate_dataclass_parameter(param)
                lines.extend(field_lines)

        return "\n".join(lines)

    def _generate_dataclass_parameter(self, param: ClickDataParam) -> List[str]:
        """Generate dataclass field with type hints and docstring."""
        lines = []

        # Determine the Python type
        py_type = param.as_string_python_type()

        # Generate field with type annotation
        field_name = self._sanitize_field_name(param.name)
        if param.is_mandatory_python():
            lines.append(f"{self.indent}{field_name}: {py_type}")
        else:
            # Determine default value
            default_value = param.as_string_default_value()
            lines.append(f"{self.indent}{field_name}: {py_type} = {default_value}")

        # Generate docstring for the field
        for docstring_line in param.to_help_string_lines(indent=self.indent):
            lines.append(docstring_line)

        lines.append("")  # Empty line between fields

        return lines

    ##############
    # internal class (wrapper with commands)
    ##############
    def _generate_wrapper_class(self) -> str:
        """Generate the main wrapper class with all command methods."""
        lines = [
            f"class {self._get_class_wrapper_name()}({self._get_class_base_name()}):",
            f'{self.indent}"""',
            f"{self.indent}This wrapper provides a Pythonic interface to the '{self.parser.script_string_package}' command-line tool,",
            f"{self.indent}allowing you to execute CLI commands programmatically without subprocess overhead.",
            f'{self.indent}"""',
            "",
            f"{self.indent}def __init__(self):",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}Initialize the ClickWrapper.",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Raises:",
            f"{self.indent}{self.indent}    ImportError: If the module cannot be imported",
            f"{self.indent}{self.indent}    AttributeError: If the specified attribute doesn't exist in the module",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}super().__init__(",
            f"{self.indent}{self.indent}{self.indent}py_import_path='{self.parser.script_string_import_path}',",
            f"{self.indent}{self.indent}{self.indent}py_import_path_attribute='{self.parser.script_string_import_attribute}'",
            f"{self.indent}{self.indent})",
            ""
        ]

        # Generate methods for all leaf commands
        for name, metadata in self.parser.commands_map.items():
            if metadata.is_leaf:
                method_lines = self._generate_wrapper_method(name, metadata.cmd_data)
                lines.append("")
                lines.extend(method_lines)

        return "\n".join(lines)

    def _generate_wrapper_method(self, cmd_name: str, cmd_data: ClickDataCommand) -> List[str]:
        """Generate a wrapper method for a specific command."""
        method_name = self._get_method_name(cmd_name)
        class_name = self._get_dataclass_name(cmd_name)
        cmd_path = cmd_name.split()

        lines = [
            f"{self.indent}# {'=' * 10} {cmd_name.upper()} COMMAND {'=' * 10}",
            "",
            (
                f"{self.indent}def cmd_{method_name}(self, opts: Optional[{class_name}] = None, stdin_input: Optional[str] = None) -> str:"
                if not cmd_data.has_mandatory else
                f"{self.indent}def cmd_{method_name}(self, opts: {class_name}, stdin_input: Optional[str] = None) -> str:"
            ),
            f'{self.indent}{self.indent}"""',
            *cmd_data.to_help_string_lines(
                indent=self.indent + self.indent,
                no_help_msg=f'Execute {cmd_name} command', 
                use_borders=False
            ),
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Args:",
            (
                f"{self.indent}{self.indent}    opts: {class_name} dataclass (uses defaults if None)"
                if not cmd_data.has_mandatory else
                f"{self.indent}{self.indent}    opts: {class_name} dataclass"
            ),
            f"{self.indent}{self.indent}    stdin_input: Optional stdin input",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Returns:",
            f"{self.indent}{self.indent}    Command output",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}if opts is None:" if not cmd_data.has_mandatory else None,
            f"{self.indent}{self.indent}{self.indent}opts = {class_name}()" if not cmd_data.has_mandatory else None,
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}args = {cmd_path}",
            f"{self.indent}{self.indent}",
        ]

        # Generate argument building logic
        arg_building = self._generate_arg_building(cmd_data)
        lines.extend(arg_building)

        lines.append(f"{self.indent}{self.indent}return self.run_command(args, input=stdin_input)")

        return [l for l in lines if l is not None]

    def _generate_arg_building(self, cmd_data) -> List[str]:
        """Generate code to build command arguments from opts."""
        lines = []

        for param in cmd_data.fnc_params:
            field_name = self._sanitize_field_name(param.name)

            # Get primary option flag
            opt_flag = self._get_option_flag(param)

            if param.param_type_name.lower() == "boolean":
                # Boolean flags
                lines.append(f"{self.indent}{self.indent}if opts.{field_name}:")
                lines.append(f"{self.indent}{self.indent}{self.indent}args.append('{opt_flag}')")
            elif param.multiple or param.nargs > 1 or param.nargs == -1:
                # Multiple values
                lines.append(f"{self.indent}{self.indent}if opts.{field_name}:")
                if "tuple" in param.as_string_python_type():
                    lines.append(f"{self.indent}{self.indent}{self.indent}for item in opts.{field_name}:")
                    lines.append(
                        f"{self.indent}{self.indent}{self.indent}{self.indent}args.extend(['{opt_flag}', item[0], item[1]])")
                else:
                    lines.append(f"{self.indent}{self.indent}{self.indent}for item in opts.{field_name}:")
                    lines.append(
                        f"{self.indent}{self.indent}{self.indent}{self.indent}args.extend(['{opt_flag}', item])")
            elif param.param_type_name.lower() == "argument":
                # Positional arguments
                lines.append(f"{self.indent}{self.indent}if opts.{field_name}:")
                lines.append(f"{self.indent}{self.indent}{self.indent}args.append(opts.{field_name})")
            else:
                # Regular opts with values
                default_check = ""
                if param.default is not None and param.default != "" and not isinstance(param.default, bool):
                    default_check = f" or opts.{field_name} != {param.as_string_default_value()}"

                lines.append(f"{self.indent}{self.indent}if opts.{field_name}{default_check}:")
                lines.append(
                    f"{self.indent}{self.indent}{self.indent}args.extend(['{opt_flag}', str(opts.{field_name})])")

            lines.append("")

        return lines

    def _get_option_flag(self, param: ClickDataParam) -> str:
        """Get the primary option flag for a parameter."""
        if param.opts:
            # Prefer long options (--xxx) over short ones (-x)
            long_opts = [opt for opt in param.opts if opt.startswith("--")]
            if long_opts:
                return long_opts[0]
            return param.opts[0]
        return f"--{param.name}"

    def _get_method_name(self, cmd_name: str) -> str:
        """Generate method name from command name."""
        # Replace spaces with underscores, make lowercase
        return cmd_name.replace(" ", "_").replace("-", "_").lower()

    def _get_class_base_name(self):
        prefix = self.parser.script_string_package.capitalize()
        return f'{prefix}{ClickImporter.__name__}'

    def _get_class_wrapper_name(self):
        prefix = self.parser.script_string_package.capitalize()
        return f'{prefix}ClickWrapper'

    ##############
    # internal helpers
    ##############

    def _sanitize_field_name(self, name: str) -> str:
        """Sanitize field name to be valid Python identifier."""
        # Handle reserved keywords
        if name in ("continue", "from", "import", "class", "for", "if", "while"):
            return f"{name}_"

        # Replace hyphens with underscores
        return name.replace("-", "_")

    def _get_dataclass_name(self, cmd_name: str) -> str:
        """Generate dataclass name from command name."""
        # Split by spaces, capitalize each part, and join
        parts = cmd_name.replace("-"," ").split()
        class_name = "".join(part.capitalize() for part in parts) + "Options"
        return class_name
