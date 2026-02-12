"""Spotify OAuth pairing flow."""

import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Tuple
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP server handler for OAuth callback."""
    
    auth_code = None
    
    def do_GET(self):
        """Handle GET request from OAuth callback."""
        # Parse query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            OAuthCallbackHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
                <html>
                <head><title>Spotify Authorization</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: green;">SUCCESS - Authorization Complete!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
                <html>
                <head><title>Spotify Authorization</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">ERROR - Authorization Failed</h1>
                    <p>No authorization code received.</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def get_authorization_url(client_id: str, redirect_uri: str, scopes: list) -> str:
    """Generate Spotify authorization URL.
    
    Args:
        client_id: Spotify client ID
        redirect_uri: OAuth redirect URI
        scopes: List of permission scopes
        
    Returns:
        str: Authorization URL
    """
    scope_str = ' '.join(scopes)
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope_str,
    }
    
    auth_url = 'https://accounts.spotify.com/authorize?' + urllib.parse.urlencode(params)
    return auth_url


def start_oauth_flow(client_id: str, redirect_uri: str) -> Optional[str]:
    """Start OAuth authorization flow and wait for callback.
    
    Args:
        client_id: Spotify client ID
        redirect_uri: OAuth redirect URI (must match Spotify app settings)
        
    Returns:
        Optional[str]: Authorization code, or None if failed
    """
    scopes = [
        'user-read-playback-state',
        'user-read-currently-playing',
        'user-modify-playback-state',
    ]
    
    auth_url = get_authorization_url(client_id, redirect_uri, scopes)
    
    logger.info("Opening browser for Spotify authorization...")
    logger.info(f"If browser doesn't open, visit: {auth_url}")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Parse redirect URI to get port
    parsed = urllib.parse.urlparse(redirect_uri)
    port = parsed.port or 8888
    
    # Start local server to receive callback
    logger.info(f"Waiting for authorization on http://localhost:{port}...")
    
    server = HTTPServer(('localhost', port), OAuthCallbackHandler)
    
    # Handle one request (the callback)
    server.handle_request()
    server.server_close()
    
    if OAuthCallbackHandler.auth_code:
        logger.info("✓ Authorization code received")
        return OAuthCallbackHandler.auth_code
    else:
        logger.error("✗ Failed to receive authorization code")
        return None
