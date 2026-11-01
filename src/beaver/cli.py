"""The `beaver` command: thin clients over the core library, reading plain files, no model.

This is the first command; #41 adds `beaver`, `capture` and `sprint`, and #50 the rest.
"""

from pathlib import Path

import typer

from beaver import __version__
from beaver.validate import validate_workspace

app = typer.Typer(
    help="Beaver: your apprenticeship workspace is plain files, and these commands read them.",
    no_args_is_help=True,
    add_completion=False,
)


def show_version(value: bool):
    if value:
        typer.echo(f"beaver {__version__}")
        raise typer.Exit()


@app.callback()
def root(
    version: bool = typer.Option(False, "--version", callback=show_version, is_eager=True, help="Show the version."),
):
    """Beaver: your apprenticeship workspace is plain files, and these commands read them."""


@app.command()
def validate(workspace: Path = typer.Argument(Path("."), help="The workspace folder to check.")):
    """Check every record, ID and wikilink in a workspace."""
    report = validate_workspace(workspace)
    typer.echo(report.render())
    raise typer.Exit(1 if report.problems else 0)


def main():
    app()
