import subprocess
from pathlib import Path

from mrkdwn_analysis import MarkdownAnalyzer
from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax

from fencechecker.config import python_language_identifiers
from fencechecker.models import ProcessedCodeBlock, ProcessedFile


def process_file(
    filepath: Path, python_binary: str, code_prefix: str | None
) -> ProcessedFile:
    """
    Process the fenced code blocks in the given filepath.

    :param filepath: Path to the file to be processed.
    :param python_binary: The python binary to run the code.
    :param code_prefix: Code to prepend to the code block source.
    :return: Metadata about the processed file.
    """
    analyzer = MarkdownAnalyzer(str(filepath))
    code_blocks = analyzer.identify_code_blocks().get("Code block", [])
    python_code_blocks = [
        code_block
        for code_block in code_blocks
        if code_block["language"] in python_language_identifiers
    ]
    completed_processes = [
        subprocess.run(
            [
                python_binary,
                "-c",
                f"{code_prefix if code_prefix else ''}{code_block['content']}",
            ],
            capture_output=True,
        )
        for code_block in python_code_blocks
    ]
    processed_code_blocks: list[ProcessedCodeBlock] = []

    for index, completed_process in enumerate(completed_processes):
        code_block = python_code_blocks[index]

        processed_code_blocks.append(
            {
                "start_line": code_block["start_line"],
                "content": code_block["content"],
                "language": code_block["language"],
                "ran_ok": completed_process.returncode == 0,
            }
        )

    return {
        "filepath": filepath,
        "code_blocks": processed_code_blocks,
        "error_count": sum(process.returncode != 0 for process in completed_processes),
    }


def report_processed_file(
    processed_file: ProcessedFile,
    console: Console,
    err_console: Console,
    only_report_errors: bool,
) -> None:
    """
    Print a report to stderr/stdout regarding the processing of the provided file.

    :param processed_file: Metadata about the processed file.
    :param console: The console used to print to stdout.
    :param err_console: The console used to print to stderr.
    :param only_report_errors: Only report errors when `True`.
    :return: Nothing.
    """
    for code_block in processed_file["code_blocks"]:
        if only_report_errors and code_block["ran_ok"]:
            continue

        syntax = Syntax(code_block["content"], "python")
        status_color = "green" if code_block["ran_ok"] else "red"
        status_title = "OK" if code_block["ran_ok"] else "Error"
        status_icon = "✔" if code_block["ran_ok"] else "✘"
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
        file_report = Panel(group)

        console.print(file_report) if code_block["ran_ok"] else err_console.print(
            file_report
        )
