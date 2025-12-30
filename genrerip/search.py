# Copyright (c) 2025-2026 iiPython

# Modules
import sys
import json
from pathlib import Path

from mutagen._file import File
from mutagen._util import MutagenError

from rapidfuzz import process, utils
from rapidfuzz.distance.Levenshtein import distance
from rich.status import Status
from rich.progress import track

from genrerip import console
from genrerip.sources import SEARCH_MODULES

# Initialization
ALLOWED_SUFFIXES = [".mp3", ".flac"]
ALLOWED_GENRES   = json.loads((Path(__file__).parent / "data/genres.json").read_text())
GENRE_MAP = {
    "edm": "EDM",
    "ebm": "EBM",
    "aor": "AOR",
    "idm": "IDM",
    "eai": "EAI",
    "rnb": "R&B",
    "ost": "Soundtrack",
    "vgm": "Video game music",
    "jpop": "j-pop",
    "8bit": "8-bit",
    "hexd": "HexD"
}
WORD_REMAP = {
    "r&b": "R&B",
    "R&b": "R&B"
}

# Handle validation of genre tags
def validate_genres(genres: list[tuple[int, str]]) -> list[str]:
    finalized_genres = []
    for score, genre in genres:
        final_name = None

        # Some genres are so short that even a distance of 2 results in major
        # inaccuracies, so in that case, look for an exact match only
        if len(genre) <= 4:
            if genre.lower() not in ALLOWED_GENRES:
                continue

            final_name = genre

        if final_name is None:
            final_name, name_distance, _ = process.extract(genre, ALLOWED_GENRES, scorer = distance, limit = 1, processor = utils.default_process)[0]
            if name_distance > 2:
                continue

        finalized_genres.append((score, final_name))

    # Auto capitalization
    finalized_genres = [genre.capitalize() for _, genre in sorted(finalized_genres, key = lambda genre: genre[0], reverse = True)]

    # Word/genre remapping
    for index, genre in enumerate(finalized_genres.copy()):
        for look, replace in WORD_REMAP.items():
            genre = genre.replace(look, replace)

        finalized_genres[index] = GENRE_MAP.get(genre.lower(), genre)

    # Deduplicate and collapse to 4 genres
    return list(dict.fromkeys(finalized_genres))[:4]

# Handle bulk file processing
def read_file(path: Path):
    try:
        audio = File(path)
        if audio is not None:
            return audio

        console.print(f"[yellow]\\[!] [bright_magenta]{path}[/] could not have its file type detected.")

    except MutagenError:
        console.print(f"[red]\\[!] [bright_magenta]{path}[/] is corrupted and cannot be read.")

def search(path: Path, enabled_search_modules: list[str]) -> None:
    music_files = {}
    with Status("[cyan]Searching for music files...") as status:
        for file in path.rglob("*"):
            if file.suffix not in ALLOWED_SUFFIXES or file.parent in music_files:
                continue

            # Read from file
            audio = read_file(file)
            if audio is None:
                continue

            if audio.get("GENRE") and "--force" not in sys.argv:
                continue

            music_files[file.parent] = audio
            status.update(f"[cyan]Searching for music files... [bright_black]({len(music_files)} albums found)")

    for album, audio in track(sorted(music_files.items(), key = lambda x: x), "[cyan]Looking up genre information...", console = console):
        genres = []
        for module in enabled_search_modules:
            SEARCH_MODULES[module](album, audio, genres)

        name = f"[bright_magenta]{album.parent.name} - {album.name}[/]"

        # Fix up the genre list
        genres = validate_genres(genres)
        if not genres:
            console.print(f"[bright_black]\\[/] No genres were found for {name}.")
            continue

        console.print(f"[green]\\[+] Fetched the following genres for {name}: {', '.join(f'[cyan]{genre}[/]' for genre in genres)}.")

        # Apply genre list
        if "--dry" in sys.argv:
            continue

        for file in album.iterdir():
            if file.suffix not in ALLOWED_SUFFIXES:
                continue

            audio = read_file(file)
            if audio is None:
                continue

            audio["GENRE"] = genres
            audio.save()
