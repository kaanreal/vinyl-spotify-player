#!/usr/bin/env python3
"""OAuth pairing script for initial Spotify authentication."""

import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from config import Config
from spotify_client import SpotifyClient


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""
    
    auth_code: str = None
    
    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        # Parse query parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'code' in params:
            CallbackHandler.auth_code = params['code'][0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <html>
            <head>
                <title>Spotify Authorization</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding-top: 100px;
                        background-color: #191414;
                        color: #ffffff;
                    }
                    .success {
                        color: #1DB954;
                        font-size: 24px;
                        font-weight: bold;
                    }
                </style>
            </head>
            <body>
                <div class="success">✓ Authorization successful!</div>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        
        elif 'error' in params:
            # Send error response
            error = params['error'][0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <html>
            <head>
                <title>Spotify Authorization</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding-top: 100px;
                        background-color: #191414;
                        color: #ffffff;
                    }}
                    .error {{
                        color: #ff0000;
                        font-size: 24px;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="error">✗ Authorization failed</div>
                <p>Error: {error}</p>
                <p>Please try again.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress request logging."""
        pass


def main():
    """Run OAuth pairing flow."""
    print("=" * 60)
    print("Vinyl Spotify Player - OAuth Pairing")
    print("=" * 60)
    print()
    
    # Load configuration
    try:
        config = Config()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Create Spotify client
    spotify = SpotifyClient(config)
    
    # Generate authorization URL
    auth_url = spotify.get_authorization_url()
    
    print("Step 1: Open this URL in your browser:")
    print()
    print(auth_url)
    print()
    print("Step 2: Log in to Spotify and authorize the application.")
    print()
    print("Step 3: You will be redirected to http://127.0.0.1:8888/callback")
    print("         (This server is now listening...)")
    print()
    
    # Start callback server
    server = HTTPServer(('127.0.0.1', 8888), CallbackHandler)
    
    print("Waiting for authorization...")
    print("Press Ctrl+C to cancel.")
    print()
    
    # Wait for callback
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    try:
        while CallbackHandler.auth_code is None:
            server.handle_request()
            
            # Check timeout
            if time.time() - start_time > timeout:
                print("\nERROR: Authorization timeout. Please try again.")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nAuthorization cancelled.")
        sys.exit(1)
    
    finally:
        server.server_close()
    
    # Exchange code for tokens
    print("Exchanging authorization code for tokens...")
    
    try:
        spotify.exchange_code_for_tokens(CallbackHandler.auth_code)
        print()
        print("✓ Success! Tokens saved to tokens.json")
        print()
        print("You can now run the main application:")
        print("  python3 main.py")
        print()
        print("Or enable the systemd service:")
        print("  sudo systemctl enable vinyl-spotify-player.service")
        print("  sudo systemctl start vinyl-spotify-player.service")
        print()
    
    except Exception as e:
        print(f"\nERROR: Failed to exchange authorization code: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
