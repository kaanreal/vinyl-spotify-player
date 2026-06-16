from __future__ import annotations

import base64
import hashlib
import secrets
import threading
from urllib.parse import parse_qs, urlparse

import requests

from config import load_config, load_tokens, save_tokens

AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPES = "user-read-playback-state user-modify-playback-state user-read-currently-playing"


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def build_auth_url(client_id: str, redirect_uri: str) -> tuple[str, str]:
    verifier, challenge = _pkce_pair()
    params = (
        f"response_type=code"
        f"&client_id={client_id}"
        f"&scope={SCOPES.replace(' ', '%20')}"
        f"&redirect_uri={redirect_uri}"
        f"&code_challenge_method=S256"
        f"&code_challenge={challenge}"
    )
    return f"{AUTHORIZE_URL}?{params}", verifier


def exchange_code(client_id: str, redirect_uri: str, code: str, verifier: str) -> dict:
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": verifier,
        },
    )
    r.raise_for_status()
    return r.json()


def refresh_access_token(client_id: str, refresh_token: str) -> dict:
    r = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
        },
    )
    r.raise_for_status()
    return r.json()


class TokenManager:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self._lock = threading.Lock()
        self._tokens = load_tokens() or {}

    def get_access_token(self) -> str | None:
        with self._lock:
            if not self._tokens:
                return None
            return self._tokens.get("access_token")

    def has_tokens(self) -> bool:
        return bool(self._tokens.get("access_token"))

    def set_tokens(self, tokens: dict) -> None:
        with self._lock:
            self._tokens = tokens
            save_tokens(tokens)

    def ensure_token(self) -> str | None:
        with self._lock:
            if not self._tokens:
                return None
            token = self._tokens["access_token"]
            refresh = self._tokens.get("refresh_token")
            if refresh:
                try:
                    new = refresh_access_token(self.client_id, refresh)
                    self._tokens = {**self._tokens, **new}
                    save_tokens(self._tokens)
                    return new.get("access_token", token)
                except Exception:
                    return token
            return token
