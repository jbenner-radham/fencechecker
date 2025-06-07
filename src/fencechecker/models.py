from pathlib import Path
from typing import TypedDict


class MarkdownAnalyzerCodeBlock(TypedDict):
    start_line: int
    content: str
    language: str


class ProcessedCodeBlock(TypedDict):
    start_line: int
    content: str
    language: str
    ran_ok: bool


class ProcessedFile(TypedDict):
    filepath: Path
    code_blocks: list[ProcessedCodeBlock]
    error_count: int
