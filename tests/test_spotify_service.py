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
    
    def test_get_recommendations_all_strategies_fail(self, service, mock_client, happy_preset):
        """Test that empty list is returned when all strategies fail."""
        # Mock search to fail
        mock_client.search_tracks.side_effect = Exception("Search failed")
        
        tracks = service.get_mood_recommendations(happy_preset, limit=10)
        
        assert tracks == []
    
    def test_get_recommendations_library_exception_falls_back(self, service, mock_client, happy_preset):
        """Test that exception in library strategy falls back to search."""
        # Mock library methods to raise exception
        mock_client.get_liked_track_ids.side_effect = Exception("Library error")
        
        # Mock search to succeed
        search_tracks = [Mock(spec=Track, track_id=f"track{i}") for i in range(10)]
        mock_client.search_tracks.return_value = search_tracks
        
        tracks = service.get_mood_recommendations(happy_preset, limit=10, use_user_library=True)
        
        # Should fall back to search
        assert len(tracks) == 10
        mock_client.search_tracks.assert_called()
    
    def test_get_recommendations_library_method_exception_falls_back(self, service, mock_client, happy_preset):
        """Test exception in _recommend_from_library itself falls back to search (lines 104-105)."""
        track_ids = ["track1", "track2"]
        
        # Mock _recommend_from_library to raise exception
        with patch.object(service, '_recommend_from_library', side_effect=Exception("Library processing error")):
            # Mock search to succeed
            search_tracks = [Track(f"track{i}", f"Song {i}", ["Artist"], "Album", "url", "uri") for i in range(10)]
            mock_client.search_tracks.return_value = search_tracks
            
            tracks = service.get_mood_recommendations(happy_preset, limit=10, use_user_library=True, user_track_ids=track_ids)
            
            # Should fall back to search
            assert len(tracks) == 10
            mock_client.search_tracks.assert_called()
    
    def test_get_recommendations_search_raises_api_error(self, service, mock_client, happy_preset):
        """Test that exception in search strategy raises APIError."""
        # Mock the internal method to raise an exception
        with patch.object(service, '_recommend_from_search', side_effect=Exception("Critical error")):
            with pytest.raises(APIError, match="Failed to generate recommendations"):
                service.get_mood_recommendations(happy_preset, limit=10, use_user_library=False)
    
    def test_recommend_from_library_empty_features(self, service, mock_client):
        """Test that empty audio features returns empty list."""
        # Mock to return empty audio features
        mock_client.get_audio_features.return_value = []
        
        happy_preset = MoodPreset("Happy", 0.8, 0.7, 0.6, 120, "Upbeat and joyful")
        track_ids = ["track1", "track2", "track3"]
        
        tracks = service._recommend_from_library(happy_preset, track_ids, limit=10)
        
        assert tracks == []
    
    def test_recommend_from_library_no_scored_tracks(self, service, mock_client):
        """Test that no scored tracks returns empty list."""
        # Mock to return features that all fail scoring
        bad_feature = Mock(spec=AudioFeatures)
        bad_feature.track_id = "track1"
        bad_feature.calculate_mood_score.side_effect = Exception("Score error")
        
        mock_client.get_audio_features.return_value = [bad_feature]
        
        happy_preset = MoodPreset("Happy", 0.8, 0.7, 0.6, 120, "Upbeat and joyful")
        tracks = service._recommend_from_library(happy_preset, ["track1"], limit=10)
        
        assert tracks == []
    
    def test_recommend_from_search_no_results(self, service, mock_client):
        """Test that no search results returns empty list."""
        # Mock search to return empty results
        mock_client.search_tracks.return_value = []
        
        happy_preset = MoodPreset("Happy", 0.8, 0.7, 0.6, 120, "Upbeat and joyful")
        tracks = service._recommend_from_search(happy_preset, limit=10)
        
        assert tracks == []


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
    
    def test_get_audio_features_safe_handles_all_failures(self, service):
        """Test that all failures in batch and individual fetching are handled."""
        mock_client = service.client
        # Mock to always fail
        mock_client.get_audio_features.side_effect = Exception("Always fails")
        
        track_ids = ["track1", "track2"]
        features = service._get_audio_features_safe(track_ids)
        
        # Should return empty list when all attempts fail
        assert features == []
    
    def test_score_tracks_skips_invalid_features(self, service):
        """Test that invalid features are skipped during scoring."""
        # Create a mock feature that will raise an exception when scoring
        bad_feature = Mock(spec=AudioFeatures)
        bad_feature.track_id = "bad_track"
        bad_feature.calculate_mood_score.side_effect = Exception("Calculation error")
        
        good_feature = AudioFeatures("good_track", 0.8, 0.7, 0.6, 120.0)
        
        target = {"valence": 0.8, "energy": 0.7, "danceability": 0.6, "tempo": 120.0}
        scored = service._score_tracks_by_mood([bad_feature, good_feature], target)
        
        # Should skip bad feature and return only good one
        assert len(scored) == 1
        assert scored[0][0] == "good_track"
    
    def test_get_tracks_in_batches_handles_failures(self, service):
        """Test that batch failures are gracefully handled."""
        mock_client = service.client
        
        # First batch succeeds, second fails
        def get_tracks_side_effect(track_ids):
            if "track1" in track_ids:
                return [Track("track1", "Song 1", ["Artist"], "Album", "url", "uri")]
            raise Exception("Batch failed")
        
        mock_client.get_tracks.side_effect = get_tracks_side_effect
        
        track_ids = ["track1", "track2", "track3"]
        tracks = service._get_tracks_in_batches(track_ids)
        
        # Should get track from successful batch
        assert len(tracks) == 1
        assert tracks[0].track_id == "track1"
    
    def test_get_tracks_in_batches_continues_on_partial_failure(self, service):
        """Test that batch processing continues even if some batches fail."""
        mock_client = service.client
        
        call_count = [0]
        def get_tracks_side_effect(track_ids):
            call_count[0] += 1
            if call_count[0] == 2:  # Second batch fails
                raise Exception("Batch 2 failed")
            return [Track(tid, f"Song {tid}", ["Artist"], "Album", "url", "uri") for tid in track_ids]
        
        mock_client.get_tracks.side_effect = get_tracks_side_effect
        
        # Create 150 track IDs (3 batches of 50)
        track_ids = [f"track{i}" for i in range(150)]
        tracks = service._get_tracks_in_batches(track_ids)
        
        # Should get tracks from batch 1 and 3, but not 2
        assert len(tracks) == 100  # 50 from batch 1 + 50 from batch 3


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
    
    def test_low_energy_mood_gets_older_year_filter(self, service):
        """Test that low energy moods get older year filters."""
        # Create a low energy mood (< 0.4)
        sad_preset = MoodPreset("Sad", valence=0.2, energy=0.3, danceability=0.2, tempo=80, description="Melancholy and reflective")
        queries = service._generate_search_queries(sad_preset)
        
        # Should include 2010-2025 year filter for low energy
        assert any("2010-2025" in q for q in queries)


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
    
    def test_get_audio_features_safe_individual_fallback_fails(self, service, mock_client):
        """Test that individual track fallback handles failures (line 200 pass statement)."""
        track_ids = ["track1", "track2"]
        
        # Batch fails, then individual calls also fail
        call_count = [0]
        def side_effect(ids):
            call_count[0] += 1
            # First call is batch (fails), subsequent calls are individual (also fail)
            raise Exception("API Error")
        
        mock_client.get_audio_features.side_effect = side_effect
        
        features = service._get_audio_features_safe(track_ids)
        
        # Should return empty list when all attempts fail
        assert features == []
        # Should have tried: 1 batch + 2 individual = 3 calls
        assert call_count[0] == 3
