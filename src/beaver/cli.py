"""The `beaver` command: thin clients over the core library, reading plain files, no model.

`beaver` on its own is the session start: what is waiting, and the one next step.
#41 adds `capture` and `sprint`, and #50 the rest of the lifecycle.
"""

from pathlib import Path

import typer

from beaver import __version__
from beaver.home import config_path, remember_home, resolve_home
from beaver.status import check_status, write_status
from beaver.validate import validate_workspace

app = typer.Typer(
    help="Beaver: your apprenticeship workspace is plain files, and these commands read them.",
    add_completion=False,
)

NO_HOME = ("No Beaver home yet. Run `beaver init` inside your workspace, "
           "or pass --home PATH.")


def show_version(value: bool):
    if value:
        typer.echo(f"beaver {__version__}")
        raise typer.Exit()


def home_or_exit(ctx):
    home = resolve_home(explicit=ctx.obj.get("home"))
    if home is None:
        typer.echo(NO_HOME)
        raise typer.Exit(1)
    return home


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    home: Path = typer.Option(None, "--home", help="Use this workspace instead of finding one."),
    version: bool = typer.Option(False, "--version", callback=show_version, is_eager=True, help="Show the version."),
):
    """Beaver: your apprenticeship workspace is plain files, and these commands read them.

    Run `beaver` on its own to see what is waiting and your next step.
    """
    ctx.obj = {"home": home}
    if ctx.invoked_subcommand is None:
        found = home_or_exit(ctx)
        status = check_status(found.path)
        write_status(found.path, status)
        typer.echo(status.render())


@app.command()
def status(ctx: typer.Context):
    """Show what is waiting and the next step, without writing anything."""
    typer.echo(check_status(home_or_exit(ctx).path).render())


@app.command()
def validate(ctx: typer.Context, workspace: Path = typer.Argument(None, help="The workspace to check; defaults to your home.")):
    """Check every record, ID and wikilink in a workspace."""
    target = workspace or getattr(resolve_home(explicit=ctx.obj.get("home")), "path", Path("."))
    report = validate_workspace(target)
    typer.echo(report.render())
    raise typer.Exit(1 if report.problems else 0)


@app.command()
def init(folder: Path = typer.Argument(Path("."), help="Your workspace folder; defaults to here.")):
    """Remember a workspace as your home, so `beaver` finds it from any folder."""
    try:
        config = remember_home(folder)
    except ValueError:
        typer.echo("That folder isn't a Beaver workspace yet: it has no beaver.yaml. "
                   "Open your fork of the template and run `beaver init` there.")
        raise typer.Exit(1)
    typer.echo(f"Home set to {folder.expanduser().resolve()} (saved in {config}).\n"
               "Run `beaver` from any folder to see what's waiting.")


@app.command()
def doctor(ctx: typer.Context):
    """Show where Beaver finds your home and what it can read there."""
    found = resolve_home(explicit=ctx.obj.get("home"))
    config = config_path()
    typer.echo(f"Config   {config} ({'saved' if config.is_file() else 'not written yet'})")
    if found is None:
        typer.echo(f"Home     not found. {NO_HOME}")
        raise typer.Exit(1)
    report = validate_workspace(found.path)
    status_file = found.path / "generated" / "status.md"
    typer.echo(f"Home     {found.path} (found by {found.found_by})\n"
               f"Records  {report.checked}, with {len(report.problems)} problem{'s' * (len(report.problems) != 1)}\n"
               f"Status   {status_file.relative_to(found.path)} ({'written' if status_file.is_file() else 'not written yet'})")


def main():
    app()
