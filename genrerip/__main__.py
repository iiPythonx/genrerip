# Copyright (c) 2025-2026 iiPython

import sys
from pathlib import Path

from genrerip import console
from genrerip.search import search

def genrerip() -> None:
    if not sys.argv[1:]:
        return console.print("[red][bold]genrerip:[/] path to music files is missing!")

    music_target = Path(sys.argv[1])
    if not music_target.is_dir():
        return console.print("[red][bold]genrerip:[/] given path is not a valid directory!")

    search(music_target, ["mbz", "lfm"])
