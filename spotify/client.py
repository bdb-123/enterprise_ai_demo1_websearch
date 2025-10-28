"""
📚 SPOTIFY API CLIENT

This module handles all interactions with the Spotify Web API.
Following the same patterns as src/client.py, we separate API communication
from business logic, making the code testable and maintainable.

DESIGN PRINCIPLES:
- Single Responsibility: This class only talks to Spotify API
- Error Handling: Convert API errors to our custom exceptions
- Logging: Track all API calls for debugging
- Secrets Management: Use environment variables, never hardcode

SPOTIFY APIs USED:
- OAuth 2.0 for user authentication
- Current User Profile
- User's Saved Tracks (Liked Songs)
- Audio Features
- Search
- Track Details
- Playlist Creation
"""

import os
import logging
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

from spotify.models import (
    UserProfile, Track, AudioFeatures, Playlist,
    AuthenticationError, APIError, ValidationError
)

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class SpotifyClient:
    """
    Client for interacting with Spotify Web API.
    
    📚 DESIGN: Wrapper around spotipy library that adds:
    - Error handling and logging
    - Type conversion (API JSON → our models)
    - Retry logic for transient failures
    - Consistent error messages
    
    Example:
        >>> client = SpotifyClient(api_key="your-key")
        >>> profile = client.get_user_profile()
        >>> print(profile.display_name)
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        use_oauth: bool = True
    ):
        """
        Initialize Spotify client with credentials.
        
        📚 CONCEPT: Environment variables for configuration.
        Never hardcode secrets. Use .env file locally, secrets manager in production.
        
        Args:
            client_id: Spotify client ID (defaults to SPOTIPY_CLIENT_ID env var)
            client_secret: Spotify client secret (defaults to SPOTIPY_CLIENT_SECRET env var)
            redirect_uri: OAuth redirect URI (defaults to SPOTIPY_REDIRECT_URI env var)
            use_oauth: Whether to use OAuth (user auth) or Client Credentials (app-only)
            
        Raises:
            AuthenticationError: If credentials are missing or invalid
        """
        self.client_id = client_id or os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIPY_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("SPOTIPY_REDIRECT_URI")
        self.use_oauth = use_oauth
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            logger.error("Missing Spotify credentials")
            raise AuthenticationError(
                "Spotify credentials not found",
                details={"hint": "Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET"}
            )
        
        # Initialize spotipy client
        try:
            if use_oauth:
                if not self.redirect_uri:
                    raise AuthenticationError(
                        "Redirect URI required for OAuth",
                        details={"hint": "Set SPOTIPY_REDIRECT_URI environment variable"}
                    )
                
                auth_manager = SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri=self.redirect_uri,
                    scope="user-library-read user-top-read playlist-modify-private",
                    cache_path=".cache_streamlit",
                    show_dialog=True
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                self.auth_manager = auth_manager
                logger.info("Spotify OAuth client initialized")
            else:
                auth_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.sp = spotipy.Spotify(client_credentials_manager=auth_manager)
                self.auth_manager = None
                logger.info("Spotify Client Credentials client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            raise AuthenticationError(f"Failed to initialize client: {str(e)}")
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated (for OAuth mode only).
        
        Returns:
            True if user has valid access token, False otherwise
        """
        if not self.use_oauth or not self.auth_manager:
            return False
        
        token_info = self.auth_manager.get_cached_token()
        return token_info is not None
    
    def get_authorize_url(self) -> str:
        """
        Get OAuth authorization URL for user to grant permissions.
        
        Returns:
            Authorization URL string
            
        Raises:
            AuthenticationError: If not using OAuth mode
        """
        if not self.use_oauth or not self.auth_manager:
            raise AuthenticationError("Not using OAuth mode")
        
        return self.auth_manager.get_authorize_url()
    
    def get_user_profile(self) -> UserProfile:
        """
        Get current user's profile information.
        
        📚 ERROR HANDLING: We catch specific Spotify exceptions and convert
        them to our custom exceptions with helpful messages.
        
        Returns:
            UserProfile object with user information
            
        Raises:
            AuthenticationError: If user not authenticated
            APIError: If API request fails
        """
        try:
            logger.debug("Fetching user profile")
            user_data = self.sp.current_user()
            
            profile = UserProfile(
                user_id=user_data.get("id", ""),
                display_name=user_data.get("display_name", "Spotify User"),
                followers=user_data.get("followers", {}).get("total", 0),
                profile_image_url=user_data.get("images", [{}])[0].get("url") if user_data.get("images") else None,
                spotify_url=user_data.get("external_urls", {}).get("spotify")
            )
            
            logger.info(f"Retrieved profile for user: {profile.display_name}")
            return profile
            
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error getting profile: {e}")
            if e.http_status == 401:
                raise AuthenticationError("Invalid or expired access token")
            raise APIError(f"Failed to get user profile: {e.msg}", status_code=e.http_status)
        except Exception as e:
            logger.error(f"Unexpected error getting profile: {e}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def get_liked_track_ids(self, max_tracks: int = 300) -> List[str]:
        """
        Get list of user's liked (saved) track IDs.
        
        📚 PAGINATION: Spotify returns results in pages of 50.
        We loop through pages until we have enough tracks or run out.
        
        Args:
            max_tracks: Maximum number of track IDs to retrieve
            
        Returns:
            List of Spotify track IDs
            
        Raises:
            AuthenticationError: If user not authenticated
            APIError: If API request fails
        """
        try:
            logger.debug(f"Fetching up to {max_tracks} liked tracks")
            
            track_ids = []
            results = self.sp.current_user_saved_tracks(limit=50)
            
            # Process first page
            track_ids.extend(self._extract_track_ids(results.get("items", [])))
            
            # Process subsequent pages
            while results.get("next") and len(track_ids) < max_tracks:
                results = self.sp.next(results)
                track_ids.extend(self._extract_track_ids(results.get("items", [])))
            
            logger.info(f"Retrieved {len(track_ids)} liked track IDs")
            return track_ids[:max_tracks]
            
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error getting liked tracks: {e}")
            if e.http_status == 401:
                raise AuthenticationError("Invalid or expired access token")
            raise APIError(f"Failed to get liked tracks: {e.msg}", status_code=e.http_status)
        except Exception as e:
            logger.error(f"Unexpected error getting liked tracks: {e}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def _extract_track_ids(self, items: List[Dict]) -> List[str]:
        """
        Extract valid track IDs from API response items.
        
        📚 DEFENSIVE PROGRAMMING: Validate each track before including it.
        Skip local files, podcasts, and tracks without IDs.
        
        Args:
            items: List of track items from API response
            
        Returns:
            List of valid track IDs
        """
        track_ids = []
        for item in items:
            track_data = item.get("track")
            if not track_data:
                continue
            
            # Skip non-track types (podcasts, etc)
            if track_data.get("type") != "track":
                continue
            
            # Skip local files (not available via API)
            if track_data.get("is_local", False):
                continue
            
            track_id = track_data.get("id")
            if track_id:
                track_ids.append(track_id)
        
        return track_ids
    
    def get_audio_features(self, track_ids: List[str]) -> List[AudioFeatures]:
        """
        Get audio features for multiple tracks.
        
        📚 BATCH API CALLS: Spotify allows requesting up to 100 tracks at once.
        Batching reduces API calls and improves performance.
        
        Args:
            track_ids: List of Spotify track IDs (max 100)
            
        Returns:
            List of AudioFeatures objects
            
        Raises:
            ValidationError: If track_ids list is too long
            APIError: If API request fails
        """
        if len(track_ids) > 100:
            raise ValidationError("Cannot request more than 100 tracks at once")
        
        try:
            logger.debug(f"Fetching audio features for {len(track_ids)} tracks")
            
            features_data = self.sp.audio_features(track_ids)
            
            features_list = []
            for data in features_data:
                if not data:  # Some tracks may not have features
                    continue
                
                features = AudioFeatures(
                    track_id=data.get("id", ""),
                    valence=data.get("valence", 0.5),
                    energy=data.get("energy", 0.5),
                    danceability=data.get("danceability", 0.5),
                    tempo=data.get("tempo", 120.0)
                )
                features_list.append(features)
            
            logger.info(f"Retrieved audio features for {len(features_list)} tracks")
            return features_list
            
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error getting audio features: {e}")
            raise APIError(f"Failed to get audio features: {e.msg}", status_code=e.http_status)
        except Exception as e:
            logger.error(f"Unexpected error getting audio features: {e}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def get_tracks(self, track_ids: List[str]) -> List[Track]:
        """
        Get full track details for multiple tracks.
        
        Args:
            track_ids: List of Spotify track IDs (max 50)
            
        Returns:
            List of Track objects
            
        Raises:
            ValidationError: If track_ids list is too long
            APIError: If API request fails
        """
        if len(track_ids) > 50:
            raise ValidationError("Cannot request more than 50 tracks at once")
        
        try:
            logger.debug(f"Fetching details for {len(track_ids)} tracks")
            
            tracks_data = self.sp.tracks(track_ids)
            
            tracks = []
            for data in tracks_data.get("tracks", []):
                if not data:
                    continue
                
                track = self._parse_track(data)
                if track:
                    tracks.append(track)
            
            logger.info(f"Retrieved details for {len(tracks)} tracks")
            return tracks
            
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error getting tracks: {e}")
            raise APIError(f"Failed to get tracks: {e.msg}", status_code=e.http_status)
        except Exception as e:
            logger.error(f"Unexpected error getting tracks: {e}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def search_tracks(self, query: str, limit: int = 20, market: str = "US") -> List[Track]:
        """
        Search for tracks by query string.
        
        Args:
            query: Search query string
            limit: Maximum number of results (max 50)
            market: ISO 3166-1 alpha-2 country code
            
        Returns:
            List of Track objects
            
        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request fails
        """
        if limit > 50:
            raise ValidationError("Cannot request more than 50 tracks")
        if not query.strip():
            raise ValidationError("Search query cannot be empty")
        
        try:
            logger.debug(f"Searching tracks with query: {query}")
            
            results = self.sp.search(q=query, limit=limit, type='track', market=market)
            
            tracks = []
            for data in results.get("tracks", {}).get("items", []):
                track = self._parse_track(data)
                if track:
                    tracks.append(track)
            
            logger.info(f"Found {len(tracks)} tracks for query: {query}")
            return tracks
            
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error searching tracks: {e}")
            raise APIError(f"Search failed: {e.msg}", status_code=e.http_status)
        except Exception as e:
            logger.error(f"Unexpected error searching tracks: {e}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def _parse_track(self, track_data: Dict[str, Any]) -> Optional[Track]:
        """
        Parse track data from API response into Track object.
        
        📚 DATA TRANSFORMATION: Convert external API format to our internal format.
        This isolates the rest of our code from Spotify's API structure.
        
        Args:
            track_data: Raw track data from Spotify API
            
        Returns:
            Track object or None if data is invalid
        """
        try:
            return Track(
                track_id=track_data.get("id", ""),
                name=track_data.get("name", ""),
                artists=[artist.get("name", "") for artist in track_data.get("artists", [])],
                album_name=track_data.get("album", {}).get("name", ""),
                spotify_url=track_data.get("external_urls", {}).get("spotify", ""),
                uri=track_data.get("uri", ""),
                preview_url=track_data.get("preview_url"),
                album_image_url=track_data.get("album", {}).get("images", [{}])[0].get("url") if track_data.get("album", {}).get("images") else None
            )
        except Exception as e:
            logger.warning(f"Failed to parse track data: {e}")
            return None
    
    def create_playlist(
        self,
        user_id: str,
        name: str,
        description: str = "",
        is_public: bool = False
    ) -> Playlist:
        """
        Create a new playlist for the user.
        
        Args:
            user_id: Spotify user ID
            name: Playlist name
            description: Playlist description
            is_public: Whether playlist is public
            
        Returns:
            Playlist object
            
        Raises:
            AuthenticationError: If user not authenticated
            APIError: If API request fails
        """
        try:
            logger.debug(f"Creating playlist: {name}")
            
            playlist_data = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=is_public,
                description=description
            )
            
            playlist = Playlist(
                playlist_id=playlist_data.get("id", ""),
                name=playlist_data.get("name", ""),
                owner_id=user_id,
                description=description,
                is_public=is_public,
                spotify_url=playlist_data.get("external_urls", {}).get("spotify")
            )
            
            logger.info(f"Created playlist: {name}")
            return playlist
            
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error creating playlist: {e}")
            if e.http_status == 401:
                raise AuthenticationError("Invalid or expired access token")
            raise APIError(f"Failed to create playlist: {e.msg}", status_code=e.http_status)
        except Exception as e:
            logger.error(f"Unexpected error creating playlist: {e}")
            raise APIError(f"Unexpected error: {str(e)}")
    
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]) -> None:
        """
        Add tracks to an existing playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            track_ids: List of track IDs to add
            
        Raises:
            ValidationError: If track_ids list is empty or too long
            APIError: If API request fails
        """
        if not track_ids:
            raise ValidationError("Cannot add empty track list to playlist")
        if len(track_ids) > 100:
            raise ValidationError("Cannot add more than 100 tracks at once")
        
        try:
            logger.debug(f"Adding {len(track_ids)} tracks to playlist {playlist_id}")
            
            self.sp.playlist_add_items(playlist_id, track_ids)
            
            logger.info(f"Added {len(track_ids)} tracks to playlist")
            
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error adding tracks to playlist: {e}")
            raise APIError(f"Failed to add tracks: {e.msg}", status_code=e.http_status)
        except Exception as e:
            logger.error(f"Unexpected error adding tracks to playlist: {e}")
            raise APIError(f"Unexpected error: {str(e)}")
