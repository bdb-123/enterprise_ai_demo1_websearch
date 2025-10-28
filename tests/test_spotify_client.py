"""
📚 TESTS FOR SPOTIFY CLIENT

Testing API client following patterns from test_client.py:
- Mock external API calls (never call real Spotify API in tests)
- Test error handling and retries
- Test data transformation (API JSON → our models)
- Test authentication flows
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import spotipy
from spotify.client import SpotifyClient
from spotify.models import (
    UserProfile, Track, AudioFeatures, Playlist,
    AuthenticationError, APIError, ValidationError
)


class TestSpotifyClientInitialization:
    """Tests for client initialization and authentication."""
    
    @patch('spotify.client.SpotifyOAuth')
    @patch('spotify.client.spotipy.Spotify')
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'test_id',
        'SPOTIPY_CLIENT_SECRET': 'test_secret',
        'SPOTIPY_REDIRECT_URI': 'http://localhost:8501'
    })
    def test_client_initialization_with_oauth(self, mock_spotify, mock_oauth):
        """Test initializing client with OAuth."""
        client = SpotifyClient()
        
        assert client.client_id == 'test_id'
        assert client.use_oauth is True
        mock_oauth.assert_called_once()
    
    @patch('spotify.client.SpotifyClientCredentials')
    @patch('spotify.client.spotipy.Spotify')
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'test_id',
        'SPOTIPY_CLIENT_SECRET': 'test_secret'
    })
    def test_client_initialization_without_oauth(self, mock_spotify, mock_creds):
        """Test initializing client without OAuth."""
        client = SpotifyClient(use_oauth=False)
        
        assert client.use_oauth is False
        mock_creds.assert_called_once()
    
    @patch.dict('os.environ', {}, clear=True)
    def test_initialization_without_credentials_raises_error(self):
        """Test that missing credentials raises AuthenticationError."""
        with pytest.raises(AuthenticationError, match="Spotify credentials not found"):
            SpotifyClient()
    
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'test_id',
        'SPOTIPY_CLIENT_SECRET': 'test_secret'
    }, clear=True)
    def test_initialization_oauth_without_redirect_uri_raises_error(self):
        """Test that OAuth without redirect URI raises AuthenticationError."""
        with pytest.raises(AuthenticationError, match="Redirect URI required"):
            SpotifyClient(use_oauth=True)
    
    @patch('spotify.client.SpotifyOAuth')
    @patch('spotify.client.spotipy.Spotify')
    @patch.dict('os.environ', {
        'SPOTIPY_CLIENT_ID': 'test_id',
        'SPOTIPY_CLIENT_SECRET': 'test_secret',
        'SPOTIPY_REDIRECT_URI': 'http://localhost:8501'
    })
    def test_initialization_failure_raises_auth_error(self, mock_spotify, mock_oauth):
        """Test that initialization failures raise AuthenticationError."""
        mock_spotify.side_effect = Exception("Connection failed")
        
        with pytest.raises(AuthenticationError, match="Failed to initialize client"):
            SpotifyClient()
    
    def test_is_authenticated_with_oauth(self):
        """Test checking authentication status with OAuth."""
        with patch('spotify.client.SpotifyOAuth') as mock_oauth, \
             patch('spotify.client.spotipy.Spotify'), \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret',
                 'SPOTIPY_REDIRECT_URI': 'http://localhost:8501'
             }):
            mock_auth = Mock()
            mock_auth.get_cached_token.return_value = {"access_token": "token"}
            mock_oauth.return_value = mock_auth
            
            client = SpotifyClient()
            client.auth_manager = mock_auth
            
            assert client.is_authenticated() is True
    
    def test_is_authenticated_without_oauth(self):
        """Test authentication check without OAuth."""
        with patch('spotify.client.SpotifyClientCredentials'), \
             patch('spotify.client.spotipy.Spotify'), \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret'
             }):
            client = SpotifyClient(use_oauth=False)
            
            assert client.is_authenticated() is False
    
    def test_get_authorize_url_success(self):
        """Test getting OAuth authorization URL."""
        with patch('spotify.client.SpotifyOAuth') as mock_oauth, \
             patch('spotify.client.spotipy.Spotify'), \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret',
                 'SPOTIPY_REDIRECT_URI': 'http://localhost:8501'
             }):
            mock_auth = Mock()
            mock_auth.get_authorize_url.return_value = "https://auth.url"
            mock_oauth.return_value = mock_auth
            
            client = SpotifyClient()
            client.auth_manager = mock_auth
            
            url = client.get_authorize_url()
            assert url == "https://auth.url"
    
    def test_get_authorize_url_without_oauth_raises_error(self):
        """Test that getting auth URL without OAuth raises error."""
        with patch('spotify.client.SpotifyClientCredentials'), \
             patch('spotify.client.spotipy.Spotify'), \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret'
             }):
            client = SpotifyClient(use_oauth=False)
            
            with pytest.raises(AuthenticationError, match="Not using OAuth mode"):
                client.get_authorize_url()


class TestUserProfile:
    """Tests for user profile retrieval."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Spotify client."""
        with patch('spotify.client.SpotifyOAuth'), \
             patch('spotify.client.spotipy.Spotify') as mock_sp, \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret',
                 'SPOTIPY_REDIRECT_URI': 'http://localhost:8501'
             }):
            client = SpotifyClient()
            client.sp = mock_sp.return_value
            yield client
    
    def test_get_user_profile_success(self, mock_client):
        """Test successfully retrieving user profile."""
        mock_client.sp.current_user.return_value = {
            "id": "user123",
            "display_name": "Test User",
            "followers": {"total": 150},
            "images": [{"url": "https://image.url"}],
            "external_urls": {"spotify": "https://spotify.com/user"}
        }
        
        profile = mock_client.get_user_profile()
        
        assert isinstance(profile, UserProfile)
        assert profile.user_id == "user123"
        assert profile.display_name == "Test User"
        assert profile.followers == 150
    
    def test_get_user_profile_minimal_data(self, mock_client):
        """Test profile with minimal data."""
        mock_client.sp.current_user.return_value = {
            "id": "user123",
            "display_name": "Test"
        }
        
        profile = mock_client.get_user_profile()
        
        assert profile.user_id == "user123"
        assert profile.followers == 0
        assert profile.profile_image_url is None
    
    def test_get_user_profile_api_error(self, mock_client):
        """Test handling API error when getting profile."""
        mock_client.sp.current_user.side_effect = spotipy.exceptions.SpotifyException(
            404, "Not Found", "User not found"
        )
        
        with pytest.raises(APIError):
            mock_client.get_user_profile()
    
    def test_get_user_profile_auth_error(self, mock_client):
        """Test handling authentication error."""
        mock_client.sp.current_user.side_effect = spotipy.exceptions.SpotifyException(
            401, "Unauthorized", "Invalid token"
        )
        
        with pytest.raises(AuthenticationError, match="Invalid or expired"):
            mock_client.get_user_profile()
    
    def test_get_user_profile_unexpected_error(self, mock_client):
        """Test handling unexpected errors."""
        mock_client.sp.current_user.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(APIError, match="Unexpected error"):
            mock_client.get_user_profile()


class TestLikedTracks:
    """Tests for liked tracks retrieval."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Spotify client."""
        with patch('spotify.client.SpotifyOAuth'), \
             patch('spotify.client.spotipy.Spotify') as mock_sp, \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret',
                 'SPOTIPY_REDIRECT_URI': 'http://localhost:8501'
             }):
            client = SpotifyClient()
            client.sp = mock_sp.return_value
            yield client
    
    def test_get_liked_track_ids_success(self, mock_client):
        """Test successfully retrieving liked track IDs."""
        mock_client.sp.current_user_saved_tracks.return_value = {
            "items": [
                {"track": {"id": "track1", "type": "track", "is_local": False}},
                {"track": {"id": "track2", "type": "track", "is_local": False}}
            ],
            "next": None
        }
        
        track_ids = mock_client.get_liked_track_ids()
        
        assert len(track_ids) == 2
        assert "track1" in track_ids
        assert "track2" in track_ids
    
    def test_get_liked_track_ids_filters_local_files(self, mock_client):
        """Test that local files are filtered out."""
        mock_client.sp.current_user_saved_tracks.return_value = {
            "items": [
                {"track": {"id": "track1", "type": "track", "is_local": False}},
                {"track": {"id": "track2", "type": "track", "is_local": True}},
                {"track": {"id": "track3", "type": "track", "is_local": False}}
            ],
            "next": None
        }
        
        track_ids = mock_client.get_liked_track_ids()
        
        assert len(track_ids) == 2
        assert "track2" not in track_ids
    
    def test_get_liked_track_ids_pagination(self, mock_client):
        """Test handling paginated results."""
        mock_client.sp.current_user_saved_tracks.return_value = {
            "items": [
                {"track": {"id": "track1", "type": "track", "is_local": False}}
            ],
            "next": "next_page_url"
        }
        mock_client.sp.next.return_value = {
            "items": [
                {"track": {"id": "track2", "type": "track", "is_local": False}}
            ],
            "next": None
        }
        
        track_ids = mock_client.get_liked_track_ids()
        
        assert len(track_ids) == 2
        mock_client.sp.next.assert_called_once()
    
    def test_get_liked_track_ids_api_error(self, mock_client):
        """Test handling API error when getting liked tracks."""
        mock_client.sp.current_user_saved_tracks.side_effect = spotipy.exceptions.SpotifyException(
            500, "Server Error", "Internal error"
        )
        
        with pytest.raises(APIError):
            mock_client.get_liked_track_ids()
    
    def test_get_liked_track_ids_auth_error(self, mock_client):
        """Test handling auth error when getting liked tracks."""
        mock_client.sp.current_user_saved_tracks.side_effect = spotipy.exceptions.SpotifyException(
            401, "Unauthorized", "Token expired"
        )
        
        with pytest.raises(AuthenticationError):
            mock_client.get_liked_track_ids()
    
    def test_get_liked_track_ids_unexpected_error(self, mock_client):
        """Test handling unexpected errors."""
        mock_client.sp.current_user_saved_tracks.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(APIError, match="Unexpected error"):
            mock_client.get_liked_track_ids()
    
    def test_get_liked_track_ids_skips_podcasts(self, mock_client):
        """Test that non-track types like podcasts are skipped."""
        mock_client.sp.current_user_saved_tracks.return_value = {
            "items": [
                {"track": {"id": "track1", "type": "track", "is_local": False}},
                {"track": {"id": "ep1", "type": "episode", "is_local": False}},  # Podcast
                {"track": {"id": "track2", "type": "track", "is_local": False}}
            ],
            "next": None
        }
        
        track_ids = mock_client.get_liked_track_ids()
        
        assert len(track_ids) == 2
        assert "ep1" not in track_ids
    
    def test_get_liked_track_ids_skips_local_files(self, mock_client):
        """Test that local files are skipped."""
        mock_client.sp.current_user_saved_tracks.return_value = {
            "items": [
                {"track": {"id": "track1", "type": "track", "is_local": False}},
                {"track": {"id": "local1", "type": "track", "is_local": True}},  # Local file
                {"track": {"id": "track2", "type": "track", "is_local": False}}
            ],
            "next": None
        }
        
        track_ids = mock_client.get_liked_track_ids()
        
        assert len(track_ids) == 2
        assert "local1" not in track_ids
    
    def test_get_liked_track_ids_skips_items_without_track_data(self, mock_client):
        """Test that items without track data are skipped."""
        mock_client.sp.current_user_saved_tracks.return_value = {
            "items": [
                {"track": {"id": "track1", "type": "track", "is_local": False}},
                {"track": None},  # Missing track data
                {"track": {"id": "track2", "type": "track", "is_local": False}}
            ],
            "next": None
        }
        
        track_ids = mock_client.get_liked_track_ids()
        
        assert len(track_ids) == 2


class TestAudioFeatures:
    """Tests for audio features retrieval."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Spotify client."""
        with patch('spotify.client.SpotifyClientCredentials'), \
             patch('spotify.client.spotipy.Spotify') as mock_sp, \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret'
             }):
            client = SpotifyClient(use_oauth=False)
            client.sp = mock_sp.return_value
            yield client
    
    def test_get_audio_features_success(self, mock_client):
        """Test successfully retrieving audio features."""
        mock_client.sp.audio_features.return_value = [
            {
                "id": "track1",
                "valence": 0.8,
                "energy": 0.7,
                "danceability": 0.6,
                "tempo": 120.0
            }
        ]
        
        features = mock_client.get_audio_features(["track1"])
        
        assert len(features) == 1
        assert isinstance(features[0], AudioFeatures)
        assert features[0].track_id == "track1"
        assert features[0].valence == 0.8
    
    def test_get_audio_features_too_many_tracks_raises_error(self, mock_client):
        """Test that requesting too many tracks raises ValidationError."""
        track_ids = [f"track{i}" for i in range(101)]
        
        with pytest.raises(ValidationError, match="Cannot request more than 100"):
            mock_client.get_audio_features(track_ids)
    
    def test_get_audio_features_skips_none_values(self, mock_client):
        """Test that None values in response are skipped."""
        mock_client.sp.audio_features.return_value = [
            {"id": "track1", "valence": 0.8, "energy": 0.7, "danceability": 0.6, "tempo": 120.0},
            None,
            {"id": "track2", "valence": 0.5, "energy": 0.5, "danceability": 0.5, "tempo": 100.0}
        ]
        
        features = mock_client.get_audio_features(["track1", "track2", "track3"])
        
        assert len(features) == 2
    
    def test_get_audio_features_api_error(self, mock_client):
        """Test handling API error when getting audio features."""
        mock_client.sp.audio_features.side_effect = spotipy.exceptions.SpotifyException(
            500, "Server Error", "Internal error"
        )
        
        with pytest.raises(APIError):
            mock_client.get_audio_features(["track1"])
    
    def test_get_audio_features_auth_error(self, mock_client):
        """Test handling auth error when getting audio features."""
        mock_client.sp.audio_features.side_effect = spotipy.exceptions.SpotifyException(
            401, "Unauthorized", "Token expired"
        )
        
        with pytest.raises(APIError, match="Token expired"):
            mock_client.get_audio_features(["track1"])
    
    def test_get_audio_features_unexpected_error(self, mock_client):
        """Test handling unexpected errors."""
        mock_client.sp.audio_features.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(APIError, match="Unexpected error"):
            mock_client.get_audio_features(["track1"])


class TestTrackRetrieval:
    """Tests for track details retrieval."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Spotify client."""
        with patch('spotify.client.SpotifyClientCredentials'), \
             patch('spotify.client.spotipy.Spotify') as mock_sp, \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret'
             }):
            client = SpotifyClient(use_oauth=False)
            client.sp = mock_sp.return_value
            yield client
    
    def test_get_tracks_success(self, mock_client):
        """Test successfully retrieving track details."""
        mock_client.sp.tracks.return_value = {
            "tracks": [
                {
                    "id": "track1",
                    "name": "Test Song",
                    "artists": [{"name": "Artist 1"}],
                    "album": {
                        "name": "Test Album",
                        "images": [{"url": "https://image.url"}]
                    },
                    "external_urls": {"spotify": "https://spotify.com"},
                    "uri": "spotify:track:1",
                    "preview_url": "https://preview.url"
                }
            ]
        }
        
        tracks = mock_client.get_tracks(["track1"])
        
        assert len(tracks) == 1
        assert isinstance(tracks[0], Track)
        assert tracks[0].name == "Test Song"
        assert tracks[0].artists == ["Artist 1"]
    
    def test_get_tracks_too_many_raises_error(self, mock_client):
        """Test that requesting too many tracks raises ValidationError."""
        track_ids = [f"track{i}" for i in range(51)]
        
        with pytest.raises(ValidationError, match="Cannot request more than 50"):
            mock_client.get_tracks(track_ids)
    
    def test_get_tracks_api_error(self, mock_client):
        """Test handling API error when getting tracks."""
        mock_client.sp.tracks.side_effect = spotipy.exceptions.SpotifyException(
            500, "Server Error", "Internal error"
        )
        
        with pytest.raises(APIError):
            mock_client.get_tracks(["track1"])
    
    def test_get_tracks_auth_error(self, mock_client):
        """Test handling auth error when getting tracks."""
        mock_client.sp.tracks.side_effect = spotipy.exceptions.SpotifyException(
            401, "Unauthorized", "Token expired"
        )
        
        with pytest.raises(APIError, match="Token expired"):
            mock_client.get_tracks(["track1"])
    
    def test_get_tracks_unexpected_error(self, mock_client):
        """Test handling unexpected errors."""
        mock_client.sp.tracks.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(APIError, match="Unexpected error"):
            mock_client.get_tracks(["track1"])
    
    def test_get_tracks_skips_none_values(self, mock_client):
        """Test that None values in tracks response are skipped."""
        mock_client.sp.tracks.return_value = {
            "tracks": [
                {
                    "id": "track1",
                    "name": "Test Song",
                    "artists": [{"name": "Artist"}],
                    "album": {"name": "Album", "images": []},
                    "external_urls": {"spotify": "url"},
                    "uri": "uri"
                },
                None,  # API returned None for this track
                {
                    "id": "track2",
                    "name": "Test Song 2",
                    "artists": [{"name": "Artist 2"}],
                    "album": {"name": "Album 2", "images": []},
                    "external_urls": {"spotify": "url2"},
                    "uri": "uri2"
                }
            ]
        }
        
        tracks = mock_client.get_tracks(["track1", "track2", "track3"])
        
        assert len(tracks) == 2
        assert tracks[0].name == "Test Song"
        assert tracks[1].name == "Test Song 2"
    
    def test_get_tracks_skips_malformed_data(self, mock_client):
        """Test that malformed track data is skipped."""
        mock_client.sp.tracks.return_value = {
            "tracks": [
                {
                    "id": "track1",
                    "name": "Good Song",
                    "artists": [{"name": "Artist"}],
                    "album": {"name": "Album", "images": []},
                    "external_urls": {"spotify": "url"},
                    "uri": "uri"
                },
                {
                    # Malformed data - missing required fields
                    "id": "bad_track"
                    # Missing name, artists, etc - will raise exception in _parse_track
                },
                {
                    "id": "track2",
                    "name": "Good Song 2",
                    "artists": [{"name": "Artist 2"}],
                    "album": {"name": "Album 2", "images": []},
                    "external_urls": {"spotify": "url2"},
                    "uri": "uri2"
                }
            ]
        }
        
        tracks = mock_client.get_tracks(["track1", "bad_track", "track2"])
        
        # Should skip the malformed track
        assert len(tracks) == 2
        assert tracks[0].name == "Good Song"
        assert tracks[1].name == "Good Song 2"


class TestSearch:
    """Tests for track search."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Spotify client."""
        with patch('spotify.client.SpotifyClientCredentials'), \
             patch('spotify.client.spotipy.Spotify') as mock_sp, \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret'
             }):
            client = SpotifyClient(use_oauth=False)
            client.sp = mock_sp.return_value
            yield client
    
    def test_search_tracks_success(self, mock_client):
        """Test successful track search."""
        mock_client.sp.search.return_value = {
            "tracks": {
                "items": [
                    {
                        "id": "track1",
                        "name": "Happy Song",
                        "artists": [{"name": "Artist"}],
                        "album": {"name": "Album", "images": []},
                        "external_urls": {"spotify": "url"},
                        "uri": "uri"
                    }
                ]
            }
        }
        
        tracks = mock_client.search_tracks("happy", limit=10)
        
        assert len(tracks) == 1
        assert tracks[0].name == "Happy Song"
    
    def test_search_empty_query_raises_error(self, mock_client):
        """Test that empty query raises ValidationError."""
        with pytest.raises(ValidationError, match="Search query cannot be empty"):
            mock_client.search_tracks("   ")
    
    def test_search_limit_too_high_raises_error(self, mock_client):
        """Test that limit over 50 raises ValidationError."""
        with pytest.raises(ValidationError, match="Cannot request more than 50"):
            mock_client.search_tracks("happy", limit=100)
    
    def test_search_tracks_api_error(self, mock_client):
        """Test handling API error when searching."""
        mock_client.sp.search.side_effect = spotipy.exceptions.SpotifyException(
            500, "Server Error", "Internal error"
        )
        
        with pytest.raises(APIError):
            mock_client.search_tracks("happy")
    
    def test_search_tracks_auth_error(self, mock_client):
        """Test handling auth error when searching."""
        mock_client.sp.search.side_effect = spotipy.exceptions.SpotifyException(
            401, "Unauthorized", "Token expired"
        )
        
        with pytest.raises(APIError, match="Token expired"):
            mock_client.search_tracks("happy")
    
    def test_search_tracks_unexpected_error(self, mock_client):
        """Test handling unexpected errors."""
        mock_client.sp.search.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(APIError, match="Unexpected error"):
            mock_client.search_tracks("happy")


class TestPlaylistOperations:
    """Tests for playlist creation and modification."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Spotify client."""
        with patch('spotify.client.SpotifyOAuth'), \
             patch('spotify.client.spotipy.Spotify') as mock_sp, \
             patch.dict('os.environ', {
                 'SPOTIPY_CLIENT_ID': 'test_id',
                 'SPOTIPY_CLIENT_SECRET': 'test_secret',
                 'SPOTIPY_REDIRECT_URI': 'http://localhost:8501'
             }):
            client = SpotifyClient()
            client.sp = mock_sp.return_value
            yield client
    
    def test_create_playlist_success(self, mock_client):
        """Test successfully creating a playlist."""
        mock_client.sp.user_playlist_create.return_value = {
            "id": "playlist123",
            "name": "My Playlist",
            "external_urls": {"spotify": "https://spotify.com/playlist"}
        }
        
        playlist = mock_client.create_playlist(
            user_id="user123",
            name="My Playlist",
            description="Test playlist"
        )
        
        assert isinstance(playlist, Playlist)
        assert playlist.playlist_id == "playlist123"
        assert playlist.name == "My Playlist"
    
    def test_add_tracks_to_playlist_success(self, mock_client):
        """Test successfully adding tracks to playlist."""
        mock_client.sp.playlist_add_items.return_value = None
        
        # Should not raise exception
        mock_client.add_tracks_to_playlist("playlist123", ["track1", "track2"])
        
        mock_client.sp.playlist_add_items.assert_called_once_with(
            "playlist123",
            ["track1", "track2"]
        )
    
    def test_add_empty_tracks_raises_error(self, mock_client):
        """Test that adding empty track list raises ValidationError."""
        with pytest.raises(ValidationError, match="Cannot add empty track list"):
            mock_client.add_tracks_to_playlist("playlist123", [])
    
    def test_add_too_many_tracks_raises_error(self, mock_client):
        """Test that adding too many tracks raises ValidationError."""
        track_ids = [f"track{i}" for i in range(101)]
        
        with pytest.raises(ValidationError, match="Cannot add more than 100"):
            mock_client.add_tracks_to_playlist("playlist123", track_ids)
    
    def test_create_playlist_api_error(self, mock_client):
        """Test handling API error when creating playlist."""
        mock_client.sp.user_playlist_create.side_effect = spotipy.exceptions.SpotifyException(
            500, "Server Error", "Internal error"
        )
        
        with pytest.raises(APIError):
            mock_client.create_playlist("user123", "My Playlist")
    
    def test_create_playlist_auth_error(self, mock_client):
        """Test handling auth error when creating playlist."""
        mock_client.sp.user_playlist_create.side_effect = spotipy.exceptions.SpotifyException(
            401, "Unauthorized", "Token expired"
        )
        
        with pytest.raises(AuthenticationError):
            mock_client.create_playlist("user123", "My Playlist")
    
    def test_create_playlist_unexpected_error(self, mock_client):
        """Test handling unexpected errors."""
        mock_client.sp.user_playlist_create.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(APIError, match="Unexpected error"):
            mock_client.create_playlist("user123", "My Playlist")
    
    def test_add_tracks_api_error(self, mock_client):
        """Test handling API error when adding tracks."""
        mock_client.sp.playlist_add_items.side_effect = spotipy.exceptions.SpotifyException(
            500, "Server Error", "Internal error"
        )
        
        with pytest.raises(APIError):
            mock_client.add_tracks_to_playlist("playlist123", ["track1"])
    
    def test_add_tracks_auth_error(self, mock_client):
        """Test handling auth error when adding tracks."""
        mock_client.sp.playlist_add_items.side_effect = spotipy.exceptions.SpotifyException(
            401, "Unauthorized", "Token expired"
        )
        
        with pytest.raises(APIError, match="Token expired"):
            mock_client.add_tracks_to_playlist("playlist123", ["track1"])
    
    def test_add_tracks_unexpected_error(self, mock_client):
        """Test handling unexpected errors."""
        mock_client.sp.playlist_add_items.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(APIError, match="Unexpected error"):
            mock_client.add_tracks_to_playlist("playlist123", ["track1"])
