import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from fencechecker.file import process_file, report_processed_file
from fencechecker.types import ProcessedCodeBlock, ProcessedFile


def app(
    filepaths: Annotated[
        list[Path],
        typer.Argument(
            show_default=False,
            help="The Markdown files to process.",
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
            help="The Python binary to use to execute code.",
        ),
    ] = "python3",
) -> None:
    console = Console()
    err_console = Console(stderr=True)
    total_errors = 0

    for filepath in filepaths:
        processed_file = process_file(filepath, python_binary=python_binary)
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


def main() -> None:
    typer.run(app)
