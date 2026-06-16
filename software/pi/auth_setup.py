#!/usr/bin/env python3
"""Headless Spotify OAuth setup — run this over SSH.

Usage:
  python3 auth_setup.py
  → Opens a URL. Copy-paste it into a browser on your laptop.
  → After authorizing, you'll get a redirect URL. Paste it back here.
"""

from __future__ import annotations

import sys

from config import load_config
from spotify_auth import build_auth_url, exchange_code


def main() -> int:
    cfg = load_config()
    cid = cfg["spotify_client_id"]
    if cid == "YOUR_SPOTIFY_CLIENT_ID":
        print("ERROR: Set your SPOTIFY_CLIENT_ID first in:")
        print(f"  {cfg['config_path']}")
        return 1

    redirect = cfg["spotify_redirect_uri"]
    url, verifier = build_auth_url(cid, redirect)

    print()
    print("=" * 60)
    print("  Step 1: Open this URL in your browser:")
    print("=" * 60)
    print(url)
    print()
    print("  Step 2: Log into Spotify and authorize the app.")
    print("  Step 3: After redirect, copy the FULL redirect URL.")
    print("          (It will start with:", redirect, ")")
    print()
    print("  Step 4: Paste the redirect URL here and press Enter:")
    print("=" * 60)
    print()

    redirect_response = sys.stdin.readline().strip()
    if not redirect_response:
        print("No input received.")
        return 1

    from urllib.parse import urlparse, parse_qs
    code = parse_qs(urlparse(redirect_response).query).get("code", [None])[0]
    if not code:
        print("ERROR: No 'code' found in the redirect URL.")
        return 1

    tokens = exchange_code(cid, redirect, code, verifier)

    from config import save_tokens
    save_tokens(tokens)
    print()
    print("✓ Authenticated! Tokens saved.")
    print("  Start the server and it will automatically fetch your music.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
