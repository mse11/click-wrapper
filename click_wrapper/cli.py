import click


@click.group()
@click.version_option()
def cli():
    "Wrapper for clAutomatic Python wrapper generator for Click CLI applications. Generate type-safe dataclasses and wrapper methods from Click command introspection"


@cli.command(name="command")
@click.argument(
    "example"
)
@click.option(
    "-o",
    "--option",
    help="An example option",
)
def first_command(example, option):
    "Command description goes here"
    click.echo("Here is some output")
