"""Spotify token management."""

import json
import time
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from app.util.paths import get_token_path
from app.util.logging import setup_logging

logger = setup_logging(__name__)


class TokenManager:
    """Manages Spotify access and refresh tokens."""
    
    def __init__(self, client_id: str, client_secret: str):
        """Initialize token manager.
        
        Args:
            client_id: Spotify client ID
            client_secret: Spotify client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_path = get_token_path()
        self._tokens = None
    
    def exchange_code_for_tokens(self, auth_code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens.
        
        Args:
            auth_code: Authorization code from OAuth flow
            redirect_uri: Redirect URI used in OAuth flow
            
        Returns:
            dict: Token response containing access_token, refresh_token, etc.
            
        Raises:
            requests.RequestException: If token exchange fails
        """
        token_url = 'https://accounts.spotify.com/api/token'
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        tokens = response.json()
        tokens['obtained_at'] = time.time()
        
        # Save tokens
        self.save_tokens(tokens)
        self._tokens = tokens
        
        logger.info("✓ Tokens obtained and saved")
        return tokens
    
    def load_tokens(self) -> Optional[Dict[str, Any]]:
        """Load tokens from disk.
        
        Returns:
            Optional[dict]: Tokens if they exist, None otherwise
        """
        if not self.token_path.exists():
            return None
        
        try:
            with open(self.token_path, 'r') as f:
                self._tokens = json.load(f)
            return self._tokens
        except Exception as e:
            logger.error(f"Failed to load tokens: {e}")
            return None
    
    def save_tokens(self, tokens: Dict[str, Any]) -> None:
        """Save tokens to disk.
        
        Args:
            tokens: Token dictionary to save
        """
        with open(self.token_path, 'w') as f:
            json.dump(tokens, f, indent=2)
    
    def get_access_token(self) -> Optional[str]:
        """Get valid access token, refreshing if necessary.
        
        Returns:
            Optional[str]: Valid access token, or None if unavailable
        """
        if self._tokens is None:
            self._tokens = self.load_tokens()
        
        if self._tokens is None:
            return None
        
        # Check if token needs refresh (expires in 3600s, refresh if < 5min remaining)
        obtained_at = self._tokens.get('obtained_at', 0)
        expires_in = self._tokens.get('expires_in', 3600)
        age = time.time() - obtained_at
        
        if age >= (expires_in - 300):  # Refresh if less than 5 minutes remaining
            logger.info("Access token expired, refreshing...")
            if not self.refresh_access_token():
                return None
        
        return self._tokens.get('access_token')
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token.
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        if self._tokens is None or 'refresh_token' not in self._tokens:
            logger.error("No refresh token available")
            return False
        
        token_url = 'https://accounts.spotify.com/api/token'
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self._tokens['refresh_token'],
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            new_tokens = response.json()
            new_tokens['obtained_at'] = time.time()
            
            # Preserve refresh token if not provided in response
            if 'refresh_token' not in new_tokens:
                new_tokens['refresh_token'] = self._tokens['refresh_token']
            
            self.save_tokens(new_tokens)
            self._tokens = new_tokens
            
            logger.info("✓ Access token refreshed")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Failed to refresh token: {e}")
            return False
    
    def has_valid_tokens(self) -> bool:
        """Check if valid tokens are available.
        
        Returns:
            bool: True if valid tokens exist
        """
        return self.get_access_token() is not None
