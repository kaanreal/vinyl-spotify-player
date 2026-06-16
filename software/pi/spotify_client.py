from __future__ import annotations

import logging

import requests
from requests.exceptions import RequestException

API_BASE = "https://api.spotify.com/v1"


class SpotifyClient:
    def __init__(self, token_manager):
        self._token_manager = token_manager

    def _headers(self) -> dict | None:
        token = self._token_manager.ensure_token()
        if not token:
            return None
        return {"Authorization": f"Bearer {token}"}

    def _get(self, path: str) -> dict | None:
        headers = self._headers()
        if not headers:
            return None
        try:
            r = requests.get(f"{API_BASE}{path}", headers=headers, timeout=10)
            if r.status_code == 204:
                return {}
            if r.status_code == 401:
                self._token_manager.ensure_token()
                return self._get(path)
            if r.status_code != 200:
                return None
            return r.json()
        except RequestException as e:
            logging.warning("Spotify API error: %s", e)
            return None

    def _put(self, path: str, body: dict | None = None) -> bool:
        headers = self._headers()
        if not headers:
            return False
        headers["Content-Type"] = "application/json"
        try:
            r = requests.put(f"{API_BASE}{path}", headers=headers, json=body, timeout=10)
            return r.status_code in (200, 201, 204)
        except RequestException as e:
            logging.warning("Spotify API error: %s", e)
            return False

    def _post(self, path: str) -> bool:
        headers = self._headers()
        if not headers:
            return False
        try:
            r = requests.post(f"{API_BASE}{path}", headers=headers, timeout=10)
            return r.status_code in (200, 201, 204)
        except RequestException as e:
            logging.warning("Spotify API error: %s", e)
            return False

    def currently_playing(self) -> dict | None:
        data = self._get("/me/player/currently-playing")
        if not data or not data.get("item"):
            return None
        item = data["item"]
        return {
            "is_playing": data.get("is_playing", False),
            "track_id": item.get("id"),
            "title": item.get("name"),
            "artists": [a["name"] for a in item.get("artists", [])],
            "album": item.get("album", {}).get("name", ""),
            "cover_url": item["album"]["images"][0]["url"]
            if item.get("album", {}).get("images")
            else None,
            "progress_ms": data.get("progress_ms", 0),
            "duration_ms": item.get("duration_ms", 0),
        }

    def play(self) -> bool:
        return self._put("/me/player/play")

    def pause(self) -> bool:
        return self._put("/me/player/pause")

    def next_track(self) -> bool:
        return self._post("/me/player/next")

    def previous_track(self) -> bool:
        return self._post("/me/player/previous")

    def transfer_playback(self, device_id: str | None = None) -> bool:
        return self._put("/me/player", {"device_ids": [device_id]} if device_id else [])
