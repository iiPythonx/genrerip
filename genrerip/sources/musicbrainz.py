# Copyright (c) 2025-2026 iiPython

# Modules
import musicbrainzngs

from genrerip import __version__, console

# Handle Musicbrainz
musicbrainzngs.set_useragent("genrerip", __version__, "ben@iipython.dev")

def format_mbz_genres(genres: list[dict[str, str]]) -> list[tuple[int, str]]:
    return [(int(g["count"]), g["name"].lower()) for g in genres]

def search_musicbrainz(path, audio, genres: list[tuple[int, str]]) -> None:
    release_group_id = audio.get("musicbrainz_releasegroupid")
    release_id = audio.get("musicbrainz_albumid")

    # Fetch release group tags
    try:
        if release_group_id:
            release_group = musicbrainzngs.get_release_group_by_id(release_group_id[0], includes = ["tags"])["release-group"]
            if "tag-list" in release_group:
                genres += format_mbz_genres(sorted(
                    release_group["tag-list"],
                    key = lambda tag: int(tag["count"]),
                    reverse = True
                ))

    except musicbrainzngs.ResponseError as e:
        console.print(f"[red]\\[-] (MusicBrainz) Response error occured on [bright_magenta]{path}[/].")
        return console.print(f"[bright_black]    -> {e}")

    # Fetch release tags
    try:
        if release_id:
            release = musicbrainzngs.get_release_by_id(release_id[0], includes = ["tags"])["release"]
            if "tag-list" in release:
                genres += format_mbz_genres(sorted(
                    release["tag-list"],
                    key = lambda tag: int(tag["count"]),
                    reverse = True
                ))

    except musicbrainzngs.ResponseError as e:
        console.print(f"[red]\\[-] (MusicBrainz) Response error occured on [bright_magenta]{path}[/].")
        return console.print(f"[bright_black]    -> {e}")
