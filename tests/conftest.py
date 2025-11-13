import pytest
from pathlib import Path
import sys

@pytest.fixture(scope="session")
def output_dir():
    """Create and return output directory."""
    output_path =  Path(__file__).parent / "generated"
    output_path.mkdir(exist_ok=True)

    # Create __init__.py to make it a package
    init_file = output_path / "__init__.py"
    if not init_file.exists():
        init_file.touch()

    # Add to Python path so imports work
    if str(output_path) not in sys.path:
        sys.path.insert(0, str(output_path))

    return output_path