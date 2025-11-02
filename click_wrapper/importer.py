import importlib

from typing import Any

class ClickImporter:

    def __init__(self, py_import_path: str, py_import_path_attribute: str = None):
        """
        Dynamically import a module or attribute from a module using string paths.

        Args:
            py_import_path: Dot-separated python module path (e.g., 'llm.cli')
            py_import_path_attribute: Optional attribute name to retrieve from the 'py_import_path' module
        """
        self.py_import_path: str = py_import_path
        self.py_import_path_attribute: str = py_import_path_attribute
        self.py_import_package: str = py_import_path.split(".")[0]

        self.click_obj_cli_main = self._import_from_string()

    def build_import_line(self):
        return (
                f'from {self.py_import_path} import {self.py_import_path_attribute}'
                if self.py_import_path_attribute else
                f'import {self.py_import_path}'
        )

    def _import_from_string(self) -> Any:

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