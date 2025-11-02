import pytest

from click_wrapper import ClickUtils

known_llm_commands = [
    'llm',
    'prompt',
    'chat',
    'keys', 'keys list', 'keys path', 'keys get', 'keys set',
    'logs', 'logs path', 'logs status', 'logs backup', 'logs on', 'logs off', 'logs list',
    'models', 'models list', 'models default', 'models options', 'models options list', 'models options show',
    'models options set', 'models options clear',
    'templates', 'templates list', 'templates show', 'templates edit', 'templates path', 'templates loaders',
    'schemas', 'schemas list', 'schemas show', 'schemas dsl',
    'tools', 'tools list',
    'aliases', 'aliases list', 'aliases set', 'aliases remove', 'aliases path',
    'fragments', 'fragments list', 'fragments set', 'fragments show', 'fragments remove', 'fragments loaders',
    'plugins',
    'install', 'uninstall',
    'embed', 'embed-multi',
    'similar',
    'embed-models', 'embed-models list', 'embed-models default',
    'collections', 'collections path', 'collections list', 'collections delete',
    'openai', 'openai models'
]

def test_api_string_imports():
    cli_obj = ClickUtils.import_from_string("llm.cli", "cli")
    module_obj = ClickUtils.import_from_string("llm.cli")

    with pytest.raises(AttributeError):
        ClickUtils.import_from_string("llm.cli", "cli_wrong_object_name")

    with pytest.raises(ImportError):
        ClickUtils.import_from_string("llm.cli_wrong_module_name")

def test_api_help_dump():
    help_string = ClickUtils.help_dump("llm.cli", "cli")
    assert help_string.startswith("\n(help)=\n## llm  --help")

def test_api_parse_cli_metadata():

    metadata = ClickUtils.parse_cli_metadata("llm.cli", "cli")
    assert sorted(known_llm_commands) == sorted(metadata['help_texts'].keys())
    assert sorted(known_llm_commands) == sorted(metadata['metadata'].keys())

def test_api_generate_wrapper_from_cli():
    output_file = ClickUtils.generate_wrapper_from_cli(
        module_import_path="llm.cli",
        module_global_attribute="cli",
        wrapper_class_name="ClickWrapper",
        output_file='out_generated.py'
    )


