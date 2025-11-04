from typing import Dict, Union, List, Tuple, Any, Optional

from click_wrapper import (
    ClickParser,
    ClickMetadata,
    ClickRunner,
    ClickParamData,
)

class ClickWrapper:
    """Generates wrapper code for Click CLI commands."""

    def __init__(self, parser: ClickParser):
        self.parser = parser
        self.indent = "    "

    @staticmethod
    def generate_wrapper_code(parser: ClickParser) -> str:
        """
        Convenience function to generate wrapper code from a parser.

        Args:
            parser: ClickParser instance with parsed commands

        Returns:
            Complete generated Python code as string
        """
        generator = ClickWrapper(parser)
        return generator.generate()

    def generate(self) -> str:
        """Generate complete wrapper code including imports, dataclasses, and methods."""
        parts = [
            self._generate_imports(),
            self._generate_base_exception(),
            self._generate_all_dataclasses(),
            self._generate_wrapper_class(),
        ]
        return "\n\n".join(parts)

    def _generate_imports(self) -> str:
        """Generate import statements."""
        return """from typing import Dict, Union, List, Tuple, Any, Optional
from dataclasses import dataclass
from click import Command
from click.testing import CliRunner"""

    def _generate_base_exception(self) -> str:
        """Generate base exception class."""
        return """class ClickWrapperError(Exception):
    \"\"\"Exception raised when cli command fails\"\"\"
    pass"""

    def _generate_all_dataclasses(self) -> str:
        """Generate dataclasses for all leaf commands."""
        dataclasses = []
        for name, metadata in self.parser.commands_map.items():
            if metadata.is_leaf:
                dataclass_code = self._generate_dataclass(name, metadata)
                dataclasses.append(dataclass_code)
        return "\n\n".join(dataclasses)

    def _generate_dataclass(self, cmd_name: str, cmd_data) -> str:
        """Generate a dataclass for a specific command."""
        class_name = self._get_dataclass_name(cmd_name)

        # Build help text for the dataclass
        class_help = cmd_data.fnc_help or cmd_data.fnc_help_short or f"Options for {cmd_name} command"

        lines = [
            "@dataclass",
            f"class {class_name}:",
            f'{self.indent}"""',
            f"{self.indent}{class_help}",
            f'{self.indent}"""',
        ]

        # Generate fields
        if not cmd_data.fnc_params:
            lines.append(f"{self.indent}pass")
        else:
            for param in cmd_data.fnc_params:
                field_lines = self._generate_field(param)
                lines.extend(field_lines)

        return "\n".join(lines)

    def _generate_field(self, param: ClickParamData) -> List[str]:
        """Generate dataclass field with type hints and docstring."""
        lines = []

        # Determine the Python type
        py_type = self._get_python_type(param)

        # Determine default value
        default_value = self._get_default_value(param)

        # Generate field with type annotation
        field_name = self._sanitize_field_name(param.name)
        lines.append(f"{self.indent}{field_name}: {py_type} = {default_value}")

        # Generate docstring for the field
        if param.help:
            lines.append(f'{self.indent}"""')
            lines.append(f"{self.indent}{param.help}")
            lines.append(f'{self.indent}"""')

        lines.append("")  # Empty line between fields

        return lines

    def _get_python_type(self, param: ClickParamData) -> str:
        """Determine Python type annotation from Click parameter."""
        base_type = None

        # Map Click types to Python types
        type_mapping = {
            "text": "str",
            "integer": "int",
            "float": "float",
            "boolean": "bool",
            "argument": "str",
            "option": "str",
        }

        base_type = type_mapping.get(param.param_type_name.lower(), "str")

        # Handle multiple values
        if param.multiple or param.nargs > 1 or param.nargs == -1:
            # Check if it's a tuple type (like attachment_types)
            if "tuple" in param.param_type_name.lower() or (
                    param.opts and any("--" in opt and len(opt.split()) > 1 for opt in param.opts)):
                base_type = f"List[Tuple[str, str]]"
            else:
                base_type = f"List[{base_type}]"

        # Make optional if not required
        if not param.required:
            base_type = f"Optional[{base_type}]"

        return base_type

    def _get_default_value(self, param: ClickParamData) -> str:
        """Get default value for field."""
        if param.multiple or param.nargs > 1 or param.nargs == -1:
            return "None"

        if param.default is not None and param.default != "":
            if isinstance(param.default, bool):
                return str(param.default)
            elif isinstance(param.default, (int, float)):
                return str(param.default)
            elif isinstance(param.default, str):
                return f'"{param.default}"'
            else:
                return "None"

        # For flags/boolean options
        if param.param_type_name.lower() == "boolean":
            return "False"

        return "None"

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
        parts = cmd_name.split()
        class_name = "".join(part.capitalize() for part in parts) + "Options"
        return class_name

    def _generate_wrapper_class(self) -> str:
        """Generate the main wrapper class with all command methods."""
        lines = [
            "class ClickWrapper:",
            f'{self.indent}"""',
            f"{self.indent}Wrapper for Click CLI operations using Click's CliRunner.",
            f"{self.indent}",
            f"{self.indent}This wrapper provides a Pythonic interface to the Click command-line tool,",
            f"{self.indent}allowing you to execute CLI commands programmatically without subprocess overhead.",
            f'{self.indent}"""',
            "",
            f"{self.indent}def __init__(self, cli_main_function: Command, cmd_base: str):",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}Initialize the ClickWrapper.",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Args:",
            f"{self.indent}{self.indent}    cli_main_function: The main CLI function object",
            f"{self.indent}{self.indent}    cmd_base: CLI tool name",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}self.runner = CliRunner()",
            f"{self.indent}{self.indent}self.cli_main_obj = cli_main_function",
            f"{self.indent}{self.indent}self.cli_base = cmd_base",
            "",
            f"{self.indent}def run_command(self, args: List[str], input: Optional[str] = None) -> str:",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}Run a CLI command and return the result.",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Args:",
            f"{self.indent}{self.indent}    args: List of command arguments",
            f"{self.indent}{self.indent}    input: Optional stdin input",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Returns:",
            f"{self.indent}{self.indent}    Result output",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Raises:",
            f"{self.indent}{self.indent}    ClickWrapperError: If command fails",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}result = self.runner.invoke(self.cli_main_obj, args, input=input)",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}if result.exit_code != 0:",
            f"{self.indent}{self.indent}{self.indent}full_cmd = [self.cli_base] + args + ([input] if input else [])",
            f'{self.indent}{self.indent}{self.indent}raise ClickWrapperError(f"""Command {{" ".join(full_cmd)}} failed: {{result.output}}""")',
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}return result.output",
        ]

        # Generate methods for all leaf commands
        for name, metadata in self.parser.commands_map.items():
            if metadata.is_leaf:
                method_lines = self._generate_method(name, metadata)
                lines.append("")
                lines.extend(method_lines)

        return "\n".join(lines)

    def _generate_method(self, cmd_name: str, cmd_data) -> List[str]:
        """Generate a wrapper method for a specific command."""
        method_name = self._get_method_name(cmd_name)
        class_name = self._get_dataclass_name(cmd_name)
        cmd_path = cmd_name.split()

        lines = [
            f"{self.indent}# {'=' * 10} {cmd_name.upper()} COMMAND {'=' * 10}",
            "",
            f"{self.indent}def {method_name}(self, options: Optional[{class_name}] = None, stdin_input: Optional[str] = None) -> str:",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}{cmd_data.fnc_help or cmd_data.fnc_help_short or f'Execute {cmd_name} command'}",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Args:",
            f"{self.indent}{self.indent}    options: {class_name} dataclass (uses defaults if None)",
            f"{self.indent}{self.indent}    stdin_input: Optional stdin input",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}Returns:",
            f"{self.indent}{self.indent}    Command output",
            f'{self.indent}{self.indent}"""',
            f"{self.indent}{self.indent}if options is None:",
            f"{self.indent}{self.indent}{self.indent}options = {class_name}()",
            f"{self.indent}{self.indent}",
            f"{self.indent}{self.indent}args = {cmd_path}",
            f"{self.indent}{self.indent}",
        ]

        # Generate argument building logic
        arg_building = self._generate_arg_building(cmd_data)
        lines.extend(arg_building)

        lines.append(f"{self.indent}{self.indent}return self.run_command(args, input=stdin_input)")

        return lines

    def _generate_arg_building(self, cmd_data) -> List[str]:
        """Generate code to build command arguments from options."""
        lines = []

        for param in cmd_data.fnc_params:
            field_name = self._sanitize_field_name(param.name)

            # Get primary option flag
            opt_flag = self._get_option_flag(param)

            if param.param_type_name.lower() == "boolean":
                # Boolean flags
                lines.append(f"{self.indent}{self.indent}if options.{field_name}:")
                lines.append(f"{self.indent}{self.indent}{self.indent}args.append('{opt_flag}')")
            elif param.multiple or param.nargs > 1 or param.nargs == -1:
                # Multiple values
                lines.append(f"{self.indent}{self.indent}if options.{field_name}:")
                if "tuple" in self._get_python_type(param).lower():
                    lines.append(f"{self.indent}{self.indent}{self.indent}for item in options.{field_name}:")
                    lines.append(
                        f"{self.indent}{self.indent}{self.indent}{self.indent}args.extend(['{opt_flag}', item[0], item[1]])")
                else:
                    lines.append(f"{self.indent}{self.indent}{self.indent}for item in options.{field_name}:")
                    lines.append(
                        f"{self.indent}{self.indent}{self.indent}{self.indent}args.extend(['{opt_flag}', item])")
            elif param.param_type_name.lower() == "argument":
                # Positional arguments
                lines.append(f"{self.indent}{self.indent}if options.{field_name}:")
                lines.append(f"{self.indent}{self.indent}{self.indent}args.append(options.{field_name})")
            else:
                # Regular options with values
                default_check = ""
                if param.default is not None and param.default != "" and not isinstance(param.default, bool):
                    default_check = f" or options.{field_name} != {self._get_default_value(param)}"

                lines.append(f"{self.indent}{self.indent}if options.{field_name}{default_check}:")
                lines.append(
                    f"{self.indent}{self.indent}{self.indent}args.extend(['{opt_flag}', str(options.{field_name})])")

            lines.append("")

        return lines

    def _get_option_flag(self, param: ClickParamData) -> str:
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

