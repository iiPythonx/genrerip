# Copyright (c) 2025-2026 iiPython

# Modules
from pathlib import Path

from mutagen._file import File
from mutagen._util import MutagenError

from rich.status import Status

from genrerip import console
from genrerip.sources import SEARCH_MODULES

# Initialization
ALLOWED_SUFFIXES = [".mp3", ".flac"]

def search(path: Path, enabled_search_modules: list[str]) -> None:
    music_files = []
    with Status("[cyan]Searching for music files...") as status:
        for file in path.rglob("*"):
            if file.suffix not in ALLOWED_SUFFIXES:
                continue

            # Read from file
            try:
                audio = File(file)
                if audio is None:
                    console.print(f"[yellow]\\[!] [bright_magenta]{file}[/] could not have its file type detected.")
                    continue

                # Load genre information from sources
                genres = []
                for module in enabled_search_modules:
                    SEARCH_MODULES[module](audio, genres)

                print("Genres:", genres)

            except MutagenError:
                console.print(f"[red]\\[!] [bright_magenta]{file}[/] is corrupted and cannot be read.")
                continue

            status.update(f"[cyan]Searching for music files... [bright_black]({len(music_files)} found)")
            break
