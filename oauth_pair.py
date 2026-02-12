"""OAuth pairing script for Spotify authorization."""

import json
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    auth_code = None

    def do_GET(self):
        """Handle GET request to callback endpoint."""
        query = urlparse(self.path).query
        params = parse_qs(query)

        if "code" in params:
            CallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Success</title></head>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Authorization Failed</h1>
                    <p>No authorization code received.</p>
                </body>
                </html>
            """)

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def get_authorization_url(client_id: str, redirect_uri: str, scopes: list) -> str:
    """Generate Spotify authorization URL.
    
    Args:
        client_id: Spotify client ID.
        redirect_uri: OAuth redirect URI.
        scopes: List of requested scopes.
    
    Returns:
        Authorization URL.
    """
    scope_string = " ".join(scopes)
    
    return (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope_string}"
    )


def exchange_code_for_tokens(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
    """Exchange authorization code for access and refresh tokens.
    
    Args:
        code: Authorization code.
        client_id: Spotify client ID.
        client_secret: Spotify client secret.
        redirect_uri: OAuth redirect URI.
    
    Returns:
        Token data dictionary.
    """
    import requests

    token_url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()

    return response.json()


def save_tokens(tokens: dict, tokens_path: Path) -> None:
    """Save tokens to file.
    
    Args:
        tokens: Token data dictionary.
        tokens_path: Path to save tokens.
    """
    token_data = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": time.time() + tokens["expires_in"]
    }

    with open(tokens_path, 'w') as f:
        json.dump(token_data, f, indent=2)

    print(f"\n✓ Tokens saved to {tokens_path}")


def main():
    """Main OAuth pairing flow."""
    print("=" * 60)
    print("Vinyl Spotify Player - OAuth Pairing")
    print("=" * 60)
    print()

    # Load configuration
    try:
        config = Config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("\nMake sure you have:")
        print("1. Copied config.json.example to config.json")
        print("2. Added your Spotify client_id and client_secret")
        sys.exit(1)

    # Required scopes
    scopes = [
        "user-read-playback-state",
        "user-read-currently-playing",
        "user-modify-playback-state"
    ]

    # Generate authorization URL
    auth_url = get_authorization_url(config.client_id, config.redirect_uri, scopes)

    print("Step 1: Authorize the application")
    print("-" * 60)
    print("\nOpen this URL in your browser:\n")
    print(auth_url)
    print()

    # Try to open browser automatically
    try:
        webbrowser.open(auth_url)
        print("✓ Browser opened automatically")
    except:
        print("! Could not open browser automatically")
        print("  Please copy and paste the URL above into your browser")

    print()
    print("Step 2: Authorize and wait for callback")
    print("-" * 60)
    print()

    # Parse redirect URI to get port
    parsed_uri = urlparse(config.redirect_uri)
    port = parsed_uri.port or 8888

    # Start callback server
    print(f"Starting callback server on port {port}...")
    print("Waiting for authorization...")
    print()

    server = HTTPServer(("127.0.0.1", port), CallbackHandler)

    # Wait for callback (with timeout)
    timeout = 300  # 5 minutes
    start_time = time.time()

    while CallbackHandler.auth_code is None:
        server.handle_request()

        if time.time() - start_time > timeout:
            print("\n✗ Timeout waiting for authorization")
            print("  Please try again")
            sys.exit(1)

    print("✓ Authorization code received")
    print()

    # Exchange code for tokens
    print("Step 3: Exchange code for tokens")
    print("-" * 60)
    print()

    try:
        tokens = exchange_code_for_tokens(
            CallbackHandler.auth_code,
            config.client_id,
            config.client_secret,
            config.redirect_uri
        )

        print("✓ Tokens received successfully")

        # Save tokens
        save_tokens(tokens, config.tokens_path)

        print()
        print("=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print()
        print("You can now run the application:")
        print("  python3 src/main.py")
        print()
        print("Or enable the systemd service for automatic startup:")
        print("  sudo systemctl enable vinyl-spotify-player.service")
        print("  sudo systemctl start vinyl-spotify-player.service")
        print()

    except Exception as e:
        print(f"\n✗ Error exchanging code for tokens: {e}")
        print("\nPlease check your:")
        print("1. Client ID and Client Secret in config.json")
        print("2. Redirect URI in config.json matches your Spotify app settings")
        sys.exit(1)


if __name__ == "__main__":
    main()
