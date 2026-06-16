#!/usr/bin/env python3
"""Vinyl Spotify Player — Web server + GPIO control."""

from __future__ import annotations

import logging
import sys
import threading
import time
from pathlib import Path

import flask
from flask_cors import CORS

from config import load_config
from gpio import GPIOHandler, TonearmState
from spotify_auth import (
    TokenManager,
    build_auth_url,
    exchange_code,
)
from spotify_client import SpotifyClient

HERE = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)

app = flask.Flask(
    __name__,
    static_folder=str(HERE / "static"),
    static_url_path="",
)
CORS(app)

cfg = load_config()
token_mgr = TokenManager(cfg["spotify_client_id"])
spotify = SpotifyClient(token_mgr)
gpio = GPIOHandler(cfg)
_verifier: str | None = None
_current: dict = {}
_current_lock = threading.Lock()


def _poll_loop() -> None:
    while True:
        track = spotify.currently_playing()
        with _current_lock:
            global _current
            _current = track or {}
        time.sleep(cfg.get("poll_interval", 2))


@app.route("/")
def index():
    return flask.send_from_directory(str(HERE / "static"), "index.html")


@app.route("/api/status")
def api_status():
    with _current_lock:
        playing = bool(_current.get("is_playing"))
        return {
            "authenticated": token_mgr.has_tokens(),
            "playing": playing,
            "track": _current,
            "tonearm": gpio.tonearm_state.value,
        }


@app.route("/api/play", methods=["POST"])
def api_play():
    ok = spotify.play()
    return {"ok": ok}


@app.route("/api/pause", methods=["POST"])
def api_pause():
    ok = spotify.pause()
    return {"ok": ok}


@app.route("/api/next", methods=["POST"])
def api_next():
    ok = spotify.next_track()
    return {"ok": ok}


@app.route("/api/prev", methods=["POST"])
def api_prev():
    ok = spotify.previous_track()
    return {"ok": ok}


@app.route("/api/motor/start", methods=["POST"])
def api_motor_start():
    gpio.set_motor(0.6)
    return {"ok": True}


@app.route("/api/motor/stop", methods=["POST"])
def api_motor_stop():
    gpio.stop_motor()
    return {"ok": True}


@app.route("/setup")
def setup_page():
    return flask.render_template_string(  # nosec
        """<!DOCTYPE html><html><body style="background:#111;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0">
        <div style="text-align:center">
        <h1>Vinyl Spotify Player</h1>
        {% if authed %}
        <p style="color:#1DB954">✓ Authenticated</p>
        {% else %}
        <a href="{{ url }}" style="display:inline-block;padding:14px 28px;background:#1DB954;color:#000;border-radius:8px;text-decoration:none;font-weight:bold">Connect Spotify</a>
        {% endif %}
        </div></body></html>""",
        authed=token_mgr.has_tokens(),
        url=flask.url_for("api_auth"),
    )


@app.route("/api/auth")
def api_auth():
    global _verifier, _last_auth_state
    url, _verifier = build_auth_url(cfg["spotify_client_id"], cfg["spotify_redirect_uri"])
    return flask.redirect(url)


@app.route("/callback")
def callback():
    code = flask.request.args.get("code")
    if not code or not _verifier:
        return "Missing code or verifier", 400
    try:
        tokens = exchange_code(cfg["spotify_client_id"], cfg["spotify_redirect_uri"], code, _verifier)
        token_mgr.set_tokens(tokens)
        global _verifier
        _verifier = None

        threading.Thread(target=_poll_loop, daemon=True).start()
        gpio.start_monitoring()

        return flask.redirect("/")
    except Exception as e:
        logging.error("Auth error: %s", e)
        return f"Auth failed: {e}", 500


@app.route("/api/cover")
def api_cover():
    with _current_lock:
        url = _current.get("cover_url")
    if url:
        return flask.redirect(url)
    return "", 204


@app.route("/health")
def health():
    return {"ok": True}


def _tonearm_cb(state: TonearmState) -> None:
    if state == TonearmState.DOWN:
        spotify.play()
    else:
        spotify.pause()


def main() -> int:
    gpio.on_tonearm_change(_tonearm_cb)

    if token_mgr.has_tokens():
        threading.Thread(target=_poll_loop, daemon=True).start()
        gpio.start_monitoring()
        logging.info("authenticated — polling started")

    host = cfg.get("host", "0.0.0.0")
    port = cfg.get("port", 8888)
    logging.info("server starting on %s:%s", host, port)

    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        gpio.cleanup()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
