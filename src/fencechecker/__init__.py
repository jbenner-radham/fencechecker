import os
import subprocess
from pathlib import Path
from typing import Annotated, TypedDict

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax
from mrkdwn_analysis import MarkdownAnalyzer


class MarkdownAnalyzerCodeBlock(TypedDict):
    start_line: int
    content: str
    language: str


class ProcessedCodeBlock(TypedDict):
    start_line: int
    content: str
    language: str
    return_code: int


class ProcessedFile(TypedDict):
    filepath: Path
    code_blocks: list[ProcessedCodeBlock]
    error_count: int


def process_file(filepath: Path, python_binary: str) -> ProcessedFile:
    analyzer = MarkdownAnalyzer(str(filepath))
    code_blocks = analyzer.identify_code_blocks().get("Code block")
    py_code_blocks = [
        code_block
        for code_block in code_blocks
        if code_block.get("language") == "python" or "python3"
    ]
    completed_processes = [
        subprocess.run(
            [python_binary, "-c", code_block.get("content")], capture_output=True
        )
        for code_block in py_code_blocks
    ]
    processed_code_blocks: list[ProcessedCodeBlock] = []

    for index, completed_process in enumerate(completed_processes):
        code_block = py_code_blocks[index]

        processed_code_blocks.append(
            {
                "start_line": code_block["start_line"],
                "content": code_block["content"],
                "language": code_block["language"],
                "return_code": completed_process.returncode,
            }
        )

    return {
        "filepath": filepath,
        "code_blocks": processed_code_blocks,
        "error_count": sum(process.returncode != 0 for process in completed_processes),
    }


def report_processed_file(
    processed_file: ProcessedFile, console: Console, only_report_errors: bool
) -> None:
    for code_block in processed_file["code_blocks"]:
        if only_report_errors and code_block["return_code"] == 0:
            continue

        syntax = Syntax(code_block["content"], "python")
        status_color = "green" if code_block["return_code"] == 0 else "red"
        status_title = "Success" if code_block["return_code"] == 0 else "Error"
        filepath = processed_file["filepath"]
        group = Group(
            f"[bold {status_color}]{status_title}[/bold {status_color}] ([link=file://{filepath.absolute()}]{filepath.absolute()}[/link] at line: {code_block['start_line']})",
            Panel(syntax),
        )
        console.print(Panel(group))


def app(
    filepaths: Annotated[
        list[Path], typer.Argument(help="The Markdown files to process.")
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
            "-b",
            help="The Python binary to use to execute code.",
        ),
    ] = "python3",
) -> None:
    console = Console()
    total_errors = 0

    for filepath in filepaths:
        processed_file = process_file(filepath, python_binary=python_binary)
        total_errors += processed_file["error_count"]

        report_processed_file(
            processed_file, console=console, only_report_errors=only_report_errors
        )

    console.print(f"{os.linesep}[bold]Total Errors: {total_errors}")

    raise typer.Exit(code=total_errors)


def main() -> None:
    typer.run(app)
