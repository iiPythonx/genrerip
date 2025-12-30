# Copyright (c) 2025-2026 iiPython

# Modules
import time
from requests import Session
from genrerip import __version__

# Initialization
SESSION = Session()
API_KEY = "974a5ebc077564f72bd639d122479d4b"  # Stolen :3
API_URL = f"https://ws.audioscrobbler.com/2.0/?method=album.gettoptags&autocorrect=1&api_key={API_KEY}&format=json"

# Handle Last.fm
def search_lastfm(audio, genres: list[tuple[int, str]]) -> None:
    parameters = ""

    # Handle data loading
    albumartist, album = audio.get("albumartist"), audio.get("album")
    if albumartist and album:
        parameters += f"&artist={albumartist[0]}&album={album[0]}"

    else:
        release_id = audio.get("musicbrainz_albumid")
        if release_id is None:
            return print("lastfm search failed, due to lacking album artist, lacking album, AND lacking mbid")

        parameters += f"&mbid={release_id[0]}"

    # Send off to hell
    response = SESSION.get(API_URL + parameters, headers = {"User-Agent": f"genrerip/{__version__} (ben@iipython.dev)"}).json()
    if response.get("error") == 29:
        print("lastfm ratelimit hit, temporarily waiting for 15 seconds")
        time.sleep(15)

    genres += [
        (genre["count"], genre["name"].lower())
        for genre in response["toptags"]["tag"]
    ]
