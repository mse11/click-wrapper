import pytest

from click_wrapper import ClickUtils

def test_api_string_imports():
    cli_obj = ClickUtils.import_from_string("llm.cli", "cli")
    module_obj = ClickUtils.import_from_string("llm.cli")

    with pytest.raises(AttributeError):
        ClickUtils.import_from_string("llm.cli", "cli_wrong_object_name")

    with pytest.raises(ImportError):
        ClickUtils.import_from_string("llm.cli_wrong_module_name")