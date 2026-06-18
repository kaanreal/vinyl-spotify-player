"""
Jukebox AirPlay metadata bridge — reads cover art from the shairport-sync
metadata pipe and writes it to a file for the UI server to serve.

Shairport-sync writes metadata to a named pipe at /tmp/shairport-sync-metadata.
The format is a binary length-delimited stream:
  - 4 bytes: length of the metadata block (big-endian, uint32)
  - N bytes: XML document describing the metadata event

The XML contains <item> elements with <code> tags identifying the type:
  - 'PICT' — picture/cover art data
  - 'asal' — album
  - 'minm' — title
  - 'asar' — artist

For PICT items, the data is base64-encoded inside a <data> tag.
"""

import base64
import logging
import os
import struct
import time
from typing import Optional

PIPE_PATH = "/tmp/shairport-sync-metadata"
OUTPUT_PATH = "/tmp/current_art.jpg"
POLL_INTERVAL = 0.5
PIPE_RECONNECT_DELAY = 2.0

logger = logging.getLogger(__name__)


def _ensure_pipe() -> Optional[int]:
    """Open the metadata pipe (blocking) for reading."""
    if not os.path.exists(PIPE_PATH):
        logger.warning("Metadata pipe %s does not exist yet, waiting...", PIPE_PATH)
        return None
    try:
        fd = os.open(PIPE_PATH, os.O_RDONLY)
        return fd
    except OSError as exc:
        logger.error("Failed to open pipe %s: %s", PIPE_PATH, exc)
        return None


def _read_length(fd: int) -> Optional[int]:
    """Read a 4-byte big-endian unsigned int from the fd."""
    raw = os.read(fd, 4)
    if len(raw) < 4:
        return None
    return struct.unpack(">I", raw)[0]


def _read_block(fd: int, length: int) -> Optional[bytes]:
    """Read exactly `length` bytes from fd."""
    chunks: list[bytes] = []
    remaining = length
    while remaining > 0:
        chunk = os.read(fd, remaining)
        if not chunk:
            return None
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _save_cover_art(data_b64: str) -> None:
    """Decode base64 image data and write to disk."""
    try:
        raw = base64.b64decode(data_b64)
        with open(OUTPUT_PATH, "wb") as f:
            f.write(raw)
        logger.info("Cover art saved (%d bytes)", len(raw))
    except Exception as exc:
        logger.error("Failed to decode/save cover art: %s", exc)


def _extract_pict(xml_bytes: bytes) -> None:
    """Parse minimal XML to find PICT items with base64-encoded data."""
    text = xml_bytes.decode("utf-8", errors="replace")

    # Split on <item> boundaries (simple parser, no full XML lib needed)
    items = text.split("</item>")
    for item in items:
        if "<code>PICT</code>" not in item:
            continue
        data_start = item.find("<data>")
        data_end = item.find("</data>")
        if data_start == -1 or data_end == -1:
            continue
        data_b64 = item[data_start + len("<data>"):data_end].strip()
        if data_b64:
            _save_cover_art(data_b64)


def _process_pipe(fd: int) -> None:
    """Continuously read metadata blocks from the pipe."""
    while True:
        length = _read_length(fd)
        if length is None:
            logger.warning("Pipe closed or read error, reopening...")
            return

        block = _read_block(fd, length)
        if block is None:
            logger.warning("Incomplete block read, reopening...")
            return

        _extract_pict(block)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] metadata_bridge: %(message)s",
    )
    logger.info("Starting AirPlay metadata bridge")

    while True:
        fd = _ensure_pipe()
        if fd is None:
            time.sleep(PIPE_RECONNECT_DELAY)
            continue

        try:
            _process_pipe(fd)
        except Exception as exc:
            logger.error("Pipe processing error: %s", exc)
        finally:
            try:
                os.close(fd)
            except OSError:
                pass

        time.sleep(PIPE_RECONNECT_DELAY)


if __name__ == "__main__":
    main()
