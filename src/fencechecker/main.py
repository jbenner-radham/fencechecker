import os
import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from fencechecker.config import default_python_binary
from fencechecker.file import process_file, report_processed_file

app = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        with open(Path(__file__).parent.resolve() / "../../pyproject.toml", "rb") as fp:
            pyproject = tomllib.load(fp)

        console = Console()
        console.print(
            f"{pyproject['project']['name']} {pyproject['project']['version']}"
        )

        raise typer.Exit(code=0)


@app.command(context_settings={"help_option_names": ["--help", "-h"]})
def main(
    filepaths: Annotated[
        list[Path],
        typer.Argument(
            help="Check these Markdown files.",
            show_default=False,
            exists=True,
            file_okay=True,
            readable=True,
        ),
    ],
    only_report_errors: Annotated[
        bool,
        typer.Option(
            "--only-report-errors", "-e", help="Only include errors when reporting."
        ),
    ] = False,
    python_binary: Annotated[
        str,
        typer.Option(
            "--python-binary",
            "-p",
            help="Use this Python binary to execute code.",
        ),
    ] = default_python_binary,
    venv_path: Annotated[
        Path | None,
        typer.Option(
            "--venv-path",
            "-V",
            help="Operate within this virtualenv.",
            show_default=False,
            exists=True,
            dir_okay=True,
            readable=True,
        ),
    ] = None,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Print version info and exit.",
            callback=version_callback,
        ),
    ] = False,
) -> None:
    """Check Python fenced code blocks in Markdown files."""
    console = Console()
    err_console = Console(stderr=True)
    total_errors = 0
    activate_this_path = (
        ""
        if venv_path is None
        else (
            venv_path / "Scripts" / "activate_this.py"
            if os.name == "nt"
            else venv_path / "bin" / "activate_this.py"
        )
    )
    code_prefix = (
        f"import runpy;runpy.run_path('{activate_this_path!s}');" if venv_path else None
    )

    if venv_path and not activate_this_path.exists():
        err_console.print(
            f"[bold red]✘ Error[/bold red]: Cannot activate virtualenv. The [bold]{activate_this_path}[/bold] path does not exist."
        )

        raise typer.Exit(code=-1)

    # TODO: Check that filepath is a Markdown file?

    # TODO: Implement asyncio to make it faster to run MD files with lots of code blocks.

    for filepath in filepaths:
        processed_file = process_file(
            filepath, python_binary=python_binary, code_prefix=code_prefix
        )
        total_errors += processed_file["error_count"]

        report_processed_file(
            processed_file,
            console=console,
            err_console=err_console,
            only_report_errors=only_report_errors,
        )

    total_errors_message = f"{os.linesep}[bold]Total Errors: {total_errors}"

    console.print(total_errors_message) if total_errors == 0 else err_console.print(
        total_errors_message
    )

    raise typer.Exit(code=total_errors)


if __name__ == "__main__":
    app()
