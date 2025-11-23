import click
from click_default_group import DefaultGroup
from typing import Optional
from click_wrapper import ClickUtils

@click.group(
    cls=DefaultGroup,
#    default="metadata",       suppressed as requires at least package name
#    default_if_no_args=True,  suppressed as requires at least package name
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option()
def cli():
    """
    CLI tool for introspecting and generating wrappers for Click applications.

    Provides utilities to analyze Click command structures, extract metadata,
    and generate documentation or wrapper code.
    """

@cli.command(name="metadata")
@click.argument("py_import_path")
@click.argument("py_import_path_attribute", required=False)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "yaml", "text"], case_sensitive=False),
    default="text",
    help="Output format for metadata"
)
def show_metadata(py_import_path: str, py_import_path_attribute: Optional[str], format: str):
    """
    Show metadata for all commands in a Click application.

    PY_IMPORT_PATH: Dot-separated python module path (e.g., 'llm.cli').
        If a simple name is provided without py_import_path_attribute (e.g., 'llm'),
        automatically expands to 'llm.__main__' with attribute 'cli'.

    PY_IMPORT_PATH_ATTRIBUTE: Optional attribute name to retrieve from the
        'py_import_path' module. When None and py_import_path is a simple
        module name, defaults to 'cli' from '__main__' module.

    Examples:
        click-wrapper metadata llm
        click-wrapper metadata llm.cli cli
        click-wrapper metadata llm.cli cli --format json
    """

    print(py_import_path, py_import_path_attribute)
    try:
        metadata = ClickUtils.commands_metadata(
            py_import_path,
            py_import_path_attribute
        )

        if format == "json":
            import json
            click.echo(json.dumps({k: str(v) for k, v in metadata.items()}, indent=2))
        elif format == "yaml":
            try:
                import yaml
                click.echo(yaml.dump({k: str(v) for k, v in metadata.items()}))
            except ImportError:
                click.echo("PyYAML not installed. Falling back to text format.", err=True)
                format = "text"

        if format == "text":
            click.echo(f"Metadata for {len(metadata)} command(s):\n")
            for name, meta in metadata.items():
                click.echo(f"{'=' * 60}")
                click.echo(f"Command: {name}")
                click.echo(f"Metadata: {meta}")
                click.echo()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

@cli.command()
@click.argument("py_import_path")
@click.argument("py_import_path_attribute", required=False)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Write help output to file instead of stdout"
)
def export_help(py_import_path: str, py_import_path_attribute: Optional[str], output: Optional[str]):
    """
    Generate comprehensive help for a Click application.

    PY_IMPORT_PATH: Dot-separated python module path (e.g., 'llm.cli').
        If a simple name is provided without py_import_path_attribute (e.g., 'llm'),
        automatically expands to 'llm.__main__' with attribute 'cli'.

    PY_IMPORT_PATH_ATTRIBUTE: Optional attribute name to retrieve from the
        'py_import_path' module. When None and py_import_path is a simple
        module name, defaults to 'cli' from '__main__' module.

    Examples:
        click-wrapper help llm
        click-wrapper help llm.cli cli
        click-wrapper help llm.cli cli --output help.txt
    """
    try:
        help_text = ClickUtils.dump_help(
            py_import_path,
            py_import_path_attribute
        )

        if output:
            with open(output, 'w') as f:
                f.write(help_text)
            click.echo(f"Help documentation written to: {output}")
        else:
            click.echo(help_text)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

@cli.command()
@click.argument("py_import_path")
@click.argument("py_import_path_attribute", required=False)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path for the generated wrapper"
)
def export_wrapper(
        py_import_path: str,
        py_import_path_attribute: Optional[str],
        output: Optional[str]
):
    """
    Generate a wrapper for a Click application.

    PY_IMPORT_PATH: Dot-separated python module path (e.g., 'llm.cli').
        If a simple name is provided without py_import_path_attribute (e.g., 'llm'),
        automatically expands to 'llm.__main__' with attribute 'cli'.

    PY_IMPORT_PATH_ATTRIBUTE: Optional attribute name to retrieve from the
        'py_import_path' module. When None and py_import_path is a simple
        module name, defaults to 'cli' from '__main__' module.

    Examples:
        click-wrapper wrapper llm
        click-wrapper wrapper llm.cli cli
        click-wrapper wrapper llm.cli cli --output wrapper.py
    """
    try:
        wrapper_code = ClickUtils.dump_wrapper(
            py_import_path,
            py_import_path_attribute,
            output
        )

        if output:
            click.echo(f"Wrapper generated successfully: {output}")
        else:
            click.echo(wrapper_code)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()