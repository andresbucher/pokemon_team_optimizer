from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "PokemonTeamOptimizer.spec"
OUTPUT_EXE = DIST_DIR / "PokemonTeamOptimizer.exe"


def _remove_if_exists(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.is_file():
        path.unlink()


def main() -> int:
    # Clean previous single-file build artifacts for predictable output.
    _remove_if_exists(OUTPUT_EXE)
    _remove_if_exists(BUILD_DIR / "PokemonTeamOptimizer")
    _remove_if_exists(SPEC_FILE)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        "PokemonTeamOptimizer",
        "--add-data",
        "data;data",
        "Main.py",
    ]

    print("Building single-file EXE...")
    print("Command:", " ".join(command))

    completed = subprocess.run(command, cwd=PROJECT_ROOT)
    if completed.returncode != 0:
        print("\nBuild failed.")
        return completed.returncode

    print(f"\nBuild complete: {OUTPUT_EXE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
