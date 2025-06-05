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


def process_file(filepath: Path) -> ProcessedFile:
    analyzer = MarkdownAnalyzer(str(filepath))
    code_blocks = analyzer.identify_code_blocks().get("Code block")
    py_code_blocks = [
        code_block
        for code_block in code_blocks
        if code_block.get("language") == "python" or "python3"
    ]
    completed_processes = [
        subprocess.run(
            ["python3", "-c", code_block.get("content")], capture_output=True
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


def report_processed_file(processed_file: ProcessedFile, console: Console) -> None:
    for code_block in processed_file["code_blocks"]:
        syntax = Syntax(code_block["content"], "python")
        status_color = "green" if code_block["return_code"] == 0 else "red"
        status_title = "Success" if code_block["return_code"] == 0 else "Error"
        filepath = processed_file["filepath"]
        group = Group(
            f"[bold {status_color}]{status_title}[/bold {status_color}] ([link=file://{filepath.absolute()}]{filepath.absolute()}[/link] at line: {code_block['start_line']})",
            Panel(syntax),
        )
        console.print(Panel(group))


def implementation(filepaths: Annotated[list[Path], typer.Argument()]) -> None:
    console = Console()
    total_errors = 0

    for filepath in filepaths:
        processed_file = process_file(filepath)
        total_errors += processed_file["error_count"]

        report_processed_file(processed_file, console)

    console.print(f"{os.linesep}[bold]Total Errors: {total_errors}")

    raise typer.Exit(code=total_errors)


def main() -> None:
    typer.run(implementation)
