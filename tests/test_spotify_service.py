"""
📚 TESTS FOR SPOTIFY RECOMMENDATION SERVICE

Testing business logic following patterns from test_search_service.py:
- Mock the client (never call real APIs)
- Test recommendation algorithms
- Test error handling and fallback strategies
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from spotify.service import RecommendationService
from spotify.models import (
    MoodPreset, Track, AudioFeatures, Playlist,
    DEFAULT_MOOD_PRESETS, APIError, ValidationError
)
from spotify.client import SpotifyClient


class TestRecommendationServiceInitialization:
    """Tests for service initialization."""
    
    def test_service_initialization(self):
        """Test creating service with client."""
        mock_client = Mock(spec=SpotifyClient)
        service = RecommendationService(mock_client)
        
        assert service.client == mock_client


class TestMoodRecommendations:
    """Tests for mood-based recommendations."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client."""
        return Mock(spec=SpotifyClient)
    
    @pytest.fixture
    def service(self, mock_client):
        """Create service with mock client."""
        return RecommendationService(mock_client)
    
    @pytest.fixture
    def happy_preset(self):
        """Return Happy mood preset."""
        return DEFAULT_MOOD_PRESETS["Happy"]
    
    def test_get_recommendations_invalid_limit_raises_error(self, service, happy_preset):
        """Test that invalid limit raises ValidationError."""
        with pytest.raises(ValidationError, match="Limit must be between"):
            service.get_mood_recommendations(happy_preset, limit=0)
        
        with pytest.raises(ValidationError, match="Limit must be between"):
            service.get_mood_recommendations(happy_preset, limit=100)
    
    def test_get_recommendations_from_search(self, service, mock_client, happy_preset):
        """Test recommendations from search when no user library."""
        # Mock search results
        mock_client.search_tracks.return_value = [
            Track("1", "Happy Song", ["Artist"], "Album", "url", "uri")
            for i in range(10)
        ]
        
        tracks = service.get_mood_recommendations(happy_preset, limit=10)
        
        assert len(tracks) == 10
        mock_client.search_tracks.assert_called()
    
    def test_get_recommendations_from_library_success(self, service, mock_client, happy_preset):
        """Test recommendations from user library."""
        track_ids = [f"track{i}" for i in range(20)]
        
        # Mock audio features
        mock_client.get_audio_features.return_value = [
            AudioFeatures(f"track{i}", 0.8, 0.7, 0.6, 120.0)
            for i in range(20)
        ]
        
        # Mock track details
        mock_client.get_tracks.return_value = [
            Track(f"track{i}", f"Song {i}", ["Artist"], "Album", "url", "uri")
            for i in range(10)
        ]
        
        tracks = service.get_mood_recommendations(
            happy_preset,
            limit=10,
            use_user_library=True,
            user_track_ids=track_ids
        )
        
        assert len(tracks) == 10
    
    def test_get_recommendations_fallback_to_search(self, service, mock_client, happy_preset):
        """Test fallback to search when library analysis fails."""
        track_ids = [f"track{i}" for i in range(20)]
        
        # Mock audio features to fail
        mock_client.get_audio_features.side_effect = Exception("API Error")
        
        # Mock search to succeed
        mock_client.search_tracks.return_value = [
            Track("1", "Song", ["Artist"], "Album", "url", "uri")
            for i in range(10)
        ]
        
        tracks = service.get_mood_recommendations(
            happy_preset,
            limit=10,
            use_user_library=True,
            user_track_ids=track_ids
        )
        
        # Should fall back to search
        assert len(tracks) == 10
        mock_client.search_tracks.assert_called()


class TestAudioFeatureScoring:
    """Tests for audio feature scoring algorithm."""
    
    @pytest.fixture
    def service(self):
        """Create service with mock client."""
        return RecommendationService(Mock(spec=SpotifyClient))
    
    def test_score_tracks_by_mood(self, service):
        """Test scoring tracks by mood features."""
        features = [
            AudioFeatures("track1", 0.9, 0.8, 0.7, 130.0),  # Close to target
            AudioFeatures("track2", 0.2, 0.2, 0.2, 80.0),   # Far from target
            AudioFeatures("track3", 0.8, 0.7, 0.6, 120.0),  # Exact match
        ]
        target = {"valence": 0.8, "energy": 0.7, "danceability": 0.6, "tempo": 120.0}
        
        scored = service._score_tracks_by_mood(features, target)
        
        # Should be sorted by score (ascending)
        assert scored[0][0] == "track3"  # Best match first
        assert scored[-1][0] == "track2"  # Worst match last
    
    def test_score_empty_features_returns_empty(self, service):
        """Test scoring empty features list."""
        target = {"valence": 0.8, "energy": 0.7, "danceability": 0.6, "tempo": 120.0}
        
        scored = service._score_tracks_by_mood([], target)
        
        assert len(scored) == 0


class TestSearchQueryGeneration:
    """Tests for search query generation."""
    
    @pytest.fixture
    def service(self):
        """Create service with mock client."""
        return RecommendationService(Mock(spec=SpotifyClient))
    
    def test_generate_search_queries_for_moods(self, service):
        """Test generating search queries for different moods."""
        happy_preset = DEFAULT_MOOD_PRESETS["Happy"]
        queries = service._generate_search_queries(happy_preset)
        
        assert len(queries) > 0
        assert any("happy" in q.lower() for q in queries)
    
    def test_queries_include_year_filters(self, service):
        """Test that queries include year filters based on energy."""
        # High energy mood should get recent year filter
        hype_preset = DEFAULT_MOOD_PRESETS["Hype"]
        queries = service._generate_search_queries(hype_preset)
        
        assert any("year" in q for q in queries)
    
    def test_fallback_query_exists(self, service):
        """Test that fallback query is included."""
        preset = DEFAULT_MOOD_PRESETS["Happy"]
        queries = service._generate_search_queries(preset)
        
        # Last query should be fallback
        assert "top hits" in queries[-1].lower() or "2024" in queries[-1]


class TestPlaylistCreation:
    """Tests for playlist creation."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client."""
        return Mock(spec=SpotifyClient)
    
    @pytest.fixture
    def service(self, mock_client):
        """Create service with mock client."""
        return RecommendationService(mock_client)
    
    def test_create_mood_playlist_success(self, service, mock_client):
        """Test successfully creating a mood playlist."""
        tracks = [
            Track("1", "Song 1", ["Artist"], "Album", "url", "uri"),
            Track("2", "Song 2", ["Artist"], "Album", "url", "uri")
        ]
        
        mock_client.create_playlist.return_value = Playlist(
            "pl123", "Mood2Music – Happy", "user123"
        )
        mock_client.add_tracks_to_playlist.return_value = None
        
        playlist = service.create_mood_playlist("user123", "Happy", tracks)
        
        assert playlist.name == "Mood2Music – Happy"
        mock_client.create_playlist.assert_called_once()
        mock_client.add_tracks_to_playlist.assert_called_once()
    
    def test_create_playlist_empty_tracks_raises_error(self, service):
        """Test that creating playlist with no tracks raises error."""
        with pytest.raises(ValidationError, match="Cannot create playlist with no tracks"):
            service.create_mood_playlist("user123", "Happy", [])
    
    def test_create_playlist_batches_large_track_lists(self, service, mock_client):
        """Test that large track lists are batched (max 100 per call)."""
        # Create 150 tracks
        tracks = [
            Track(str(i), f"Song {i}", ["Artist"], "Album", "url", "uri")
            for i in range(150)
        ]
        
        mock_client.create_playlist.return_value = Playlist(
            "pl123", "Mood2Music – Happy", "user123"
        )
        mock_client.add_tracks_to_playlist.return_value = None
        
        playlist = service.create_mood_playlist("user123", "Happy", tracks)
        
        # Should be called twice (100 + 50)
        assert mock_client.add_tracks_to_playlist.call_count == 2


class TestGenreRetrieval:
    """Tests for genre retrieval."""
    
    @pytest.fixture
    def service(self):
        """Create service with mock client."""
        return RecommendationService(Mock(spec=SpotifyClient))
    
    def test_get_available_genres_returns_list(self, service):
        """Test that get_available_genres returns a list."""
        genres = service.get_available_genres()
        
        assert isinstance(genres, list)
        assert len(genres) > 0
    
    def test_genres_include_common_types(self, service):
        """Test that common genres are included."""
        genres = service.get_available_genres()
        
        assert "pop" in genres
        assert "rock" in genres
        assert "hip-hop" in genres
        assert "jazz" in genres


class TestBatchOperations:
    """Tests for batch operation helpers."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client."""
        return Mock(spec=SpotifyClient)
    
    @pytest.fixture
    def service(self, mock_client):
        """Create service with mock client."""
        return RecommendationService(mock_client)
    
    def test_get_tracks_in_batches(self, service, mock_client):
        """Test getting tracks in batches of 50."""
        track_ids = [str(i) for i in range(75)]
        
        # Mock returns different tracks for each batch
        def mock_get_tracks(ids):
            return [Track(id, f"Song {id}", ["Artist"], "Album", "url", "uri") for id in ids]
        
        mock_client.get_tracks.side_effect = mock_get_tracks
        
        tracks = service._get_tracks_in_batches(track_ids)
        
        assert len(tracks) == 75
        assert mock_client.get_tracks.call_count == 2  # 50 + 25
    
    def test_get_audio_features_safe_handles_errors(self, service, mock_client):
        """Test that audio feature retrieval handles errors gracefully."""
        track_ids = [str(i) for i in range(150)]
        
        # First call succeeds, second fails
        mock_client.get_audio_features.side_effect = [
            [AudioFeatures(str(i), 0.5, 0.5, 0.5, 120.0) for i in range(100)],
            Exception("API Error")
        ]
        
        features = service._get_audio_features_safe(track_ids)
        
        # Should return partial results
        assert len(features) == 100
