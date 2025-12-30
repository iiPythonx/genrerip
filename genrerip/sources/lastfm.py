# Copyright (c) 2025-2026 iiPython

# Modules
import time
from requests import Session
from genrerip import __version__, console

# Initialization
SESSION = Session()
API_KEY = "974a5ebc077564f72bd639d122479d4b"  # Stolen :3
API_URL = f"https://ws.audioscrobbler.com/2.0/?method=album.gettoptags&autocorrect=1&api_key={API_KEY}&format=json"

# Handle Last.fm
def search_lastfm(path, audio, genres: list[tuple[int, str]]) -> None:
    parameters = ""

    # Handle data loading
    albumartist, album = audio.get("albumartist"), audio.get("album")
    if albumartist and album:
        parameters += f"&artist={albumartist[0]}&album={album[0]}"

    else:
        release_id = audio.get("musicbrainz_albumid")
        if release_id is None:
            return console.print(f"[red]\\[-] (LastFM) No album/artist/mbid preset on [bright_magenta]{path}[/], cannot search.")

        parameters += f"&mbid={release_id[0]}"

    # Send off to hell
    response = SESSION.get(API_URL + parameters, headers = {"User-Agent": f"genrerip/{__version__} (ben@iipython.dev)"}).json()
    if response.get("error") == 29:
        console.print(f"[red]\\[-] (LastFM) Ratelimit hit for [bright_magenta]{path}[/], waiting [blue]15s[/].")
        time.sleep(15)
        return search_lastfm(path, audio, genres)

    if "toptags" not in response:
        console.print(f"[red]\\[-] (LastFM) No tags were found for [bright_magenta]{path}[/].")
        return console.print(f"[bright_black]    -> Error code {response['error']}, Message: {response['message']}")

    genres += [
        (genre["count"] * 0.16, genre["name"].lower())
        for genre in response["toptags"]["tag"]
    ]
