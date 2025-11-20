import click
from click_default_group import DefaultGroup
from typing import Optional
from click_wrapper import ClickUtils

@click.group(
    cls=DefaultGroup,
    default="prompt", # TODO
    default_if_no_args=True,
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
@click.argument("py_import_path_attribute")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "yaml", "text"], case_sensitive=False),
    default="text",
    help="Output format for metadata"
)
def show_metadata(py_import_path: str, py_import_path_attribute: str, format: str):
    """
    Show metadata for all commands in a Click application.

    PY_IMPORT_PATH: Module path (e.g., 'llm.cli')

    PY_IMPORT_PATH_ATTRIBUTE: Attribute name (e.g., 'cli')

    Examples:

        click-wrapper metadata llm.cli cli

        click-wrapper metadata llm.cli cli --format json
    """
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
@click.argument("py_import_path_attribute")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Write help output to file instead of stdout"
)
def export_help(py_import_path: str, py_import_path_attribute: str, output: Optional[str]):
    """
    Generate comprehensive help for a Click application.

    PY_IMPORT_PATH: Module path (e.g., 'llm.cli')

    PY_IMPORT_PATH_ATTRIBUTE: Attribute name (e.g., 'cli')

    Examples:

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
@click.argument("py_import_path_attribute")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path for the generated wrapper"
)
def export_wrapper(
        py_import_path: str,
        py_import_path_attribute: str,
        output: Optional[str]
):
    """
    Generate a wrapper for a Click application.

    PY_IMPORT_PATH: Module path (e.g., 'llm.cli')

    PY_IMPORT_PATH_ATTRIBUTE: Attribute name (e.g., 'cli')

    Examples:

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
