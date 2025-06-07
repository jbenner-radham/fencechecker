import subprocess
from pathlib import Path

from mrkdwn_analysis import MarkdownAnalyzer
from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax

from fencechecker.types import ProcessedFile, ProcessedCodeBlock


def process_file(filepath: Path, python_binary: str) -> ProcessedFile:
    analyzer = MarkdownAnalyzer(str(filepath))
    code_blocks = analyzer.identify_code_blocks().get("Code block")
    py_code_blocks = [
        code_block
        for code_block in code_blocks
        if code_block["language"] in ("python", "python3", "py", "py3")
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
        status_title = "OK" if code_block["return_code"] == 0 else "Error"
        status_icon = "✔" if code_block["return_code"] == 0 else "✘"
        filepath = processed_file["filepath"]
        status_markup = (
            f"[bold {status_color}]{status_icon} {status_title}[/bold {status_color}]"
        )
        file_link_markup = (
            f"[link=file://{filepath.absolute()}]{filepath.absolute()}[/link]"
        )
        file_line_markup = f"line: {code_block['start_line']}"
        file_info_markup = f"({file_link_markup} at {file_line_markup})"
        group = Group(f"{status_markup} {file_info_markup}", Panel(syntax))

        console.print(Panel(group))
