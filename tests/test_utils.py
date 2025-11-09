import pytest

from click_wrapper import (
    ClickUtils,
    ClickRunner,
    ClickRunnerError,
    ClickImporter,
)

known_llm_commands = [
    '', # refers to main 'llm'
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

known_llm_commands_full = [
    " ".join(["llm"] + [c] if c != '' else ["llm"]) for c in known_llm_commands
]

def test_api_string_imports():
    cli_obj = ClickUtils.import_from_string(
        py_import_path="llm.cli",
        py_import_path_attribute="cli"
    )
    module_obj = ClickUtils.import_from_string(py_import_path="llm.cli")

    with pytest.raises(AttributeError):
        ClickUtils.import_from_string(
            py_import_path="llm.cli",
            py_import_path_attribute="cli_WRONG_OBJ_NAME"
        )

    with pytest.raises(ImportError):
        ClickUtils.import_from_string(
            py_import_path="llm.cli_WRONG_MODULE_NAME",
            py_import_path_attribute="cli"
        )

def test_api_metadata_commands_names():
    commands_names = ClickUtils.commands_names(
        "llm.cli",
        "cli",
        full_path=False)
    assert sorted(known_llm_commands) == sorted(commands_names)

    commands_names = ClickUtils.commands_names(
        "llm.cli",
        "cli",
        full_path=True)
    assert sorted(known_llm_commands_full) == sorted(commands_names)

def test_api_dump_help():
    help_string = ClickUtils.dump_help(
        py_import_path="llm.cli",
        py_import_path_attribute="cli"
    )
    assert help_string.startswith("\n(help)=\n## llm  --help")
    print(help_string)

def test_api_dump_wrapper():
    help_string = ClickUtils.dump_wrapper(
        py_import_path="llm.cli",
        py_import_path_attribute="cli",
        output_file="output_wrapper.py"
    )
    #assert help_string.startswith("\n(help)=\n## llm  --help")
    # print(help_string)

def test_api_parse_cli_metadata():
    metadata = ClickUtils.commands_metadata(
        py_import_path="llm.cli",
        py_import_path_attribute="cli"
    )
    # print()
    # import pprint
    # pprint.pprint(metadata, sort_dicts=False)
    # assert sorted(known_llm_commands) == sorted(metadata['help_texts'].keys())
    # assert sorted(known_llm_commands) == sorted(metadata['metadata'].keys())

def test_runner():
    importer = ClickImporter(
        py_import_path="llm.cli",
        py_import_path_attribute="cli",
    )

    runner = ClickRunner(
        cli_main_function=importer.click_obj_cli_main,
        cmd_base=importer.py_import_package,
    )

    output = runner.run_command(["--help"])
    # print(output)
    contain_string = 'Access Large Language Models from the command-line'
    assert contain_string in output, "Not found in help"

    with pytest.raises(ClickRunnerError):
        output = runner.run_command(["--helperMEEE"])