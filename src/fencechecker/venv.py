import os
from pathlib import Path


def autodiscover_venv_path(filepath: Path) -> Path | None:
    for parent in filepath.resolve().parents:
        venv_candidate_path = parent / ".venv"

        if venv_candidate_path.exists():
            return venv_candidate_path

    return None


def get_activate_this_path(venv_path: Path) -> Path:
    venv_bin_path_part = "Scripts" if os.name == "nt" else "bin"

    return venv_path / venv_bin_path_part / "activate_this.py"


def get_activate_this_path_and_code_prefix(venv_path: Path) -> (Path, str):
    activate_this_path = get_activate_this_path(venv_path)

    return activate_this_path, f"import runpy;runpy.run_path('{activate_this_path!s}');"


def validate_activate_this_path(activate_this_path: Path) -> str | None:
    cannot_activate_venv_msg = (
        "[bold red]✘ Error[/bold red]: Cannot activate virtual environment."
    )

    if not activate_this_path.exists():
        return (
            cannot_activate_venv_msg
            + f" The [bold]{activate_this_path}[/bold] path does not exist."
        )

    if not activate_this_path.is_file():
        return (
            cannot_activate_venv_msg
            + f" The [bold]{activate_this_path}[/bold] path is not a file."
        )

    if not os.access(activate_this_path, os.R_OK):
        return (
            cannot_activate_venv_msg
            + f" The [bold]{activate_this_path}[/bold] path is not readable."
        )

    return None
