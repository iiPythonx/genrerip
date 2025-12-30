# Copyright (c) 2025-2026 iiPython

from .musicbrainz import search_musicbrainz
from .lastfm import search_lastfm

SEARCH_MODULES = {"mbz": search_musicbrainz, "lfm": search_lastfm}
