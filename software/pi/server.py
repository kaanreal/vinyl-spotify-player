"""Jukebox UI server — Flask application serving the playback UI."""

import base64
import json
import logging
import os
import queue
import subprocess
import threading
import time
from typing import Any, Dict, Optional

from flask import Flask, Response, jsonify, send_from_directory, stream_with_context

logger = logging.getLogger(__name__)

app: Flask = Flask(__name__)

UI_DIR = os.path.dirname(os.path.abspath(__file__))

# Thread-safe shared metadata store
_metadata_lock = threading.Lock()
_metadata: Dict[str, Any] = {
    "title": "",
    "artist": "",
    "album": "",
    "art_url": "",
    "paused": True,
    "source": "",
    "active": False,
}
_real_art_url: str = ""
_art_mtime: float = 0.0

# Cache
_cache_ts: float = 0.0
_cache_ttl: float = 0.5

TRANSPARENT_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAA"
    "ABJRU5ErkJggg=="
)

# ── SSE (Server-Sent Events) ─────────────────────────────────────────────────

_sse_queues: list["queue.Queue[dict]"] = []
_sse_lock = threading.Lock()
_sse_watcher_started = False


def _sse_broadcast() -> None:
    """Force-refresh metadata and push to every connected SSE client."""
    global _cache_ts
    _cache_ts = 0.0
    _refresh_metadata()
    with _metadata_lock:
        payload = _metadata.copy()
    with _sse_lock:
        dead: list[queue.Queue] = []
        for q in _sse_queues:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _sse_queues.remove(q)


def _start_sse_watcher() -> None:
    """Daemon thread: follow playerctl status changes and broadcast via SSE."""
    global _sse_watcher_started
    if _sse_watcher_started:
        return
    _sse_watcher_started = True

    def _watch() -> None:
        while True:
            try:
                proc = subprocess.Popen(
                    ["playerctl", "--follow", "status"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                logger.info("SSE watcher: playerctl --follow started")
                for line in proc.stdout:
                    status = line.strip()
                    if status in ("Playing", "Paused", "Stopped"):
                        _sse_broadcast()
                proc.wait()
                logger.warning(
                    "SSE watcher: playerctl exited (code %d), restarting...",
                    proc.returncode,
                )
            except FileNotFoundError:
                logger.error("SSE watcher: playerctl not found, giving up")
                return
            except Exception as exc:
                logger.error("SSE watcher error: %s", exc)
            time.sleep(2)

    threading.Thread(target=_watch, daemon=True).start()


@app.route("/events")
def sse_events() -> Response:
    _start_sse_watcher()

    q: queue.Queue = queue.Queue(maxsize=10)
    with _sse_lock:
        _sse_queues.append(q)

    def generate() -> str:
        try:
            # Send current state immediately on connect
            with _metadata_lock:
                yield f"data: {json.dumps(_metadata)}\n\n"

            while True:
                try:
                    data = q.get(timeout=30)
                    yield f"data: {json.dumps(data)}\n\n"
                except queue.Empty:
                    yield "data: heartbeat\n\n"
        except GeneratorExit:
            pass
        except BrokenPipeError:
            pass
        finally:
            with _sse_lock:
                try:
                    _sse_queues.remove(q)
                except ValueError:
                    pass

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _run_playerctl(args: list[str], timeout: int = 2) -> Optional[str]:
    try:
        result = subprocess.run(
            ["playerctl"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _detect_active_player() -> Optional[str]:
    players_out = _run_playerctl(["-l"])
    if not players_out:
        return None
    players = [p.strip() for p in players_out.splitlines() if p.strip()]

    # Prefer a player that is actively Playing
    for player in players:
        status = _run_playerctl(["--player", player, "status"])
        if status == "Playing":
            return player

    return players[0] if players else None


def _read_metadata_from_player(player: str) -> Dict[str, Any]:
    global _real_art_url, _art_mtime
    title = _run_playerctl(["--player", player, "metadata", "title"]) or ""
    artist = _run_playerctl(["--player", player, "metadata", "artist"]) or ""
    album = _run_playerctl(["--player", player, "metadata", "album"]) or ""
    art_url = _run_playerctl(["--player", player, "metadata", "mpris:artUrl"]) or ""

    with _metadata_lock:
        if art_url != _real_art_url:
            _real_art_url = art_url
            _art_mtime = time.time()

    # Determine source from player name
    source = "airplay" if "shairport" in player.lower() else "spotify"

    status = _run_playerctl(["--player", player, "status"]) or "Paused"
    paused = status.lower() != "playing"

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "art_url": "/art",
        "art_mtime": _art_mtime,
        "paused": paused,
        "source": source,
        "active": True,
    }


def _find_art_file(art_url: str) -> Optional[bytes]:
    if not art_url:
        return None

    # MPRIS artUrl may be a local file path
    local_path = art_url.replace("file://", "")
    if os.path.isfile(local_path):
        try:
            with open(local_path, "rb") as f:
                return f.read()
        except OSError:
            pass

    # Fall back to the bridge-written file
    bridge_path = "/tmp/current_art.jpg"
    if os.path.isfile(bridge_path):
        try:
            with open(bridge_path, "rb") as f:
                return f.read()
        except OSError:
            pass

    return None


def _refresh_metadata() -> None:
    """Poll playerctl and update the shared metadata store."""
    global _metadata, _real_art_url, _cache_ts
    now = time.monotonic()
    if now - _cache_ts < _cache_ttl:
        return
    _cache_ts = now

    player = _detect_active_player()
    if player is None:
        with _metadata_lock:
            _metadata = {
                "title": "",
                "artist": "",
                "album": "",
                "art_url": "",
                "art_mtime": 0.0,
                "paused": True,
                "source": _metadata.get("source", ""),
                "active": False,
            }
            _real_art_url = ""
            _art_mtime = 0.0
        return

    new_meta = _read_metadata_from_player(player)
    with _metadata_lock:
        _metadata.update(new_meta)


def _toggle_playback() -> None:
    """Toggle play/pause on the active player."""
    player = _detect_active_player()
    if player is None:
        return
    _run_playerctl(["--player", player, "play-pause"])


@app.route("/")
def index() -> Response:
    return send_from_directory(UI_DIR, "index.html")


@app.route("/status")
def status() -> Response:
    _refresh_metadata()
    with _metadata_lock:
        return jsonify(_metadata.copy())


@app.route("/art")
def art() -> Response:
    _refresh_metadata()
    with _metadata_lock:
        real_url = _real_art_url

    art_data = _find_art_file(real_url)
    if art_data is not None:
        return Response(art_data, mimetype="image/jpeg", headers={"Cache-Control": "no-cache"})

    return Response(TRANSPARENT_PNG, mimetype="image/png", headers={"Cache-Control": "no-cache"})


@app.route("/toggle")
def toggle() -> Response:
    global _cache_ts
    _toggle_playback()
    _cache_ts = 0.0  # force fresh playerctl read
    _refresh_metadata()
    with _metadata_lock:
        return jsonify(_metadata.copy())


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    port = int(os.environ.get("UI_PORT", "8080"))
    logger.info("Starting Jukebox UI on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
