import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from fencechecker.file import process_file, report_processed_file

app = typer.Typer()


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
    ] = "python3",
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
) -> None:
    console = Console()
    err_console = Console(stderr=True)
    total_errors = 0
    activate_this_path = (
        venv_path / "Scripts" / "activate_this.py"
        if os.name == "nt"
        else venv_path / "bin" / "activate_this.py"
    )
    code_prefix = (
        f"import runpy;runpy.run_path('{activate_this_path!s}');" if venv_path else None
    )

    if venv_path and not activate_this_path.exists():
        err_console.print(
            f"[bold red]✘ Error[/bold red]: Cannot activate virtualenv. The [bold]{activate_this_path}[/bold] path does not exist."
        )

        raise typer.Exit(code=-1)

    # TODO: Check that filepath is a Markdown file.

    # TODO: What if a Markdown file doesn't have any code blocks?

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
