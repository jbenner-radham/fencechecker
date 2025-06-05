import subprocess
import sys
from pprint import pprint
from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax
from mrkdwn_analysis import MarkdownAnalyzer


def main() -> None:
    analyzer = MarkdownAnalyzer("./TEST.md")
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
    console = Console()

    for index, process in enumerate(completed_processes):
        code_block = py_code_blocks[index]
        syntax = Syntax(code_block.get("content"), "python")

        if process.returncode == 0:
            group = Group(
                f"[bold green]Success[/bold green] [italic](at line: {code_block.get('start_line')})",
                Panel(syntax),
            )
            console.print(Panel(group))
        else:
            group = Group(
                f"[bold red]Error[/bold red] [italic](at line: {code_block.get('start_line')})",
                Panel(syntax),
            )
            console.print(Panel(group))
            # console.print(Panel(syntax, title="[bold red]Error", title_align="left", subtitle=f"at line: {code_block.get('start_line')}", subtitle_align="right"))

    error_count = sum(1 for process in completed_processes if process.returncode != 0)

    console.print(f"[bold]Total Errors: {error_count}")

    sys.exit(error_count)
