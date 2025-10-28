"""
📚 TESTS FOR SPOTIFY MODELS

Following TDD principles from test_models.py, we test:
- Object creation and validation
- Dataclass immutability
- Custom methods and calculations
- Error conditions

TEST STRUCTURE:
- TestClassName: One class per model being tested
- test_method_name: Descriptive names that explain what's being tested
- Arrange-Act-Assert: Clear test structure
"""

import pytest
from spotify.models import (
    MoodPreset, UserProfile, Track, AudioFeatures, Playlist,
    DEFAULT_MOOD_PRESETS, SpotifyError, AuthenticationError,
    APIError, ValidationError
)


class TestMoodPreset:
    """Tests for MoodPreset dataclass."""
    
    def test_create_valid_preset(self):
        """Test creating a mood preset with valid values."""
        preset = MoodPreset(
            name="Test",
            valence=0.8,
            energy=0.7,
            danceability=0.6,
            tempo=120,
            description="Test mood"
        )
        
        assert preset.name == "Test"
        assert preset.valence == 0.8
        assert preset.energy == 0.7
        assert preset.danceability == 0.6
        assert preset.tempo == 120
    
    def test_preset_immutability(self):
        """Test that presets are immutable (frozen=True)."""
        preset = MoodPreset("Test", 0.5, 0.5, 0.5, 100, "Test")
        
        with pytest.raises(AttributeError):
            preset.valence = 0.9
    
    def test_invalid_valence_raises_error(self):
        """Test that invalid valence raises ValueError."""
        with pytest.raises(ValueError, match="Valence must be between 0 and 1"):
            MoodPreset("Test", 1.5, 0.5, 0.5, 100, "Test")
    
    def test_invalid_energy_raises_error(self):
        """Test that invalid energy raises ValueError."""
        with pytest.raises(ValueError, match="Energy must be between 0 and 1"):
            MoodPreset("Test", 0.5, -0.1, 0.5, 100, "Test")
    
    def test_invalid_danceability_raises_error(self):
        """Test that invalid danceability raises ValueError."""
        with pytest.raises(ValueError, match="Danceability must be between 0 and 1"):
            MoodPreset("Test", 0.5, 0.5, 1.5, 100, "Test")
    
    def test_invalid_tempo_raises_error(self):
        """Test that invalid tempo raises ValueError."""
        with pytest.raises(ValueError, match="Tempo must be between 60 and 200"):
            MoodPreset("Test", 0.5, 0.5, 0.5, 300, "Test")
    
    def test_to_dict_conversion(self):
        """Test converting preset to dictionary."""
        preset = MoodPreset("Happy", 0.8, 0.7, 0.6, 120, "Joyful")
        result = preset.to_dict()
        
        assert result == {
            "valence": 0.8,
            "energy": 0.7,
            "danceability": 0.6,
            "tempo": 120
        }


class TestUserProfile:
    """Tests for UserProfile dataclass."""
    
    def test_create_profile_with_required_fields(self):
        """Test creating profile with only required fields."""
        profile = UserProfile(
            user_id="user123",
            display_name="Test User"
        )
        
        assert profile.user_id == "user123"
        assert profile.display_name == "Test User"
        assert profile.followers == 0
        assert profile.profile_image_url is None
    
    def test_create_profile_with_all_fields(self):
        """Test creating profile with all fields."""
        profile = UserProfile(
            user_id="user123",
            display_name="Test User",
            followers=150,
            profile_image_url="https://image.url",
            spotify_url="https://spotify.com"
        )
        
        assert profile.followers == 150
        assert profile.profile_image_url == "https://image.url"
    
    def test_empty_user_id_raises_error(self):
        """Test that empty user_id raises ValueError."""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            UserProfile(user_id="", display_name="Test")
    
    def test_empty_display_name_raises_error(self):
        """Test that empty display_name raises ValueError."""
        with pytest.raises(ValueError, match="display_name cannot be empty"):
            UserProfile(user_id="user123", display_name="")


class TestTrack:
    """Tests for Track dataclass."""
    
    def test_create_track_with_required_fields(self):
        """Test creating track with required fields."""
        track = Track(
            track_id="track123",
            name="Test Song",
            artists=["Artist 1"],
            album_name="Test Album",
            spotify_url="https://spotify.com/track",
            uri="spotify:track:123"
        )
        
        assert track.track_id == "track123"
        assert track.name == "Test Song"
        assert track.artists == ["Artist 1"]
    
    def test_create_track_with_multiple_artists(self):
        """Test track with multiple artists."""
        track = Track(
            track_id="track123",
            name="Collaboration",
            artists=["Artist 1", "Artist 2", "Artist 3"],
            album_name="Album",
            spotify_url="https://url",
            uri="uri"
        )
        
        assert len(track.artists) == 3
    
    def test_empty_track_id_raises_error(self):
        """Test that empty track_id raises ValueError."""
        with pytest.raises(ValueError, match="track_id cannot be empty"):
            Track("", "Name", ["Artist"], "Album", "url", "uri")
    
    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Track("id", "", ["Artist"], "Album", "url", "uri")
    
    def test_empty_artists_raises_error(self):
        """Test that empty artists list raises ValueError."""
        with pytest.raises(ValueError, match="must have at least one artist"):
            Track("id", "Name", [], "Album", "url", "uri")


class TestAudioFeatures:
    """Tests for AudioFeatures dataclass."""
    
    def test_create_audio_features(self):
        """Test creating audio features."""
        features = AudioFeatures(
            track_id="track123",
            valence=0.8,
            energy=0.7,
            danceability=0.6,
            tempo=120.0
        )
        
        assert features.track_id == "track123"
        assert features.valence == 0.8
        assert features.tempo == 120.0
    
    def test_calculate_mood_score_perfect_match(self):
        """Test mood score calculation with perfect match."""
        features = AudioFeatures("id", 0.8, 0.7, 0.6, 120.0)
        target = {"valence": 0.8, "energy": 0.7, "danceability": 0.6, "tempo": 120.0}
        
        score = features.calculate_mood_score(target)
        
        assert score == 0.0  # Perfect match = 0 score
    
    def test_calculate_mood_score_with_differences(self):
        """Test mood score calculation with feature differences."""
        features = AudioFeatures("id", 0.8, 0.7, 0.6, 120.0)
        target = {"valence": 0.6, "energy": 0.5, "danceability": 0.4, "tempo": 100.0}
        
        score = features.calculate_mood_score(target)
        
        assert score > 0  # Different features = positive score
        # Score = |0.8-0.6|*2 + |0.7-0.5|*1.5 + |0.6-0.4|*1.5 + |120-100|/100
        # Score = 0.4 + 0.3 + 0.3 + 0.2 = 1.2
        assert abs(score - 1.2) < 0.01
    
    def test_valence_weighting_in_score(self):
        """Test that valence is weighted higher in score calculation."""
        features = AudioFeatures("id", 0.8, 0.5, 0.5, 120.0)
        
        # Same difference in valence vs energy
        score_valence = features.calculate_mood_score({
            "valence": 0.7, "energy": 0.5, "danceability": 0.5, "tempo": 120.0
        })
        score_energy = features.calculate_mood_score({
            "valence": 0.8, "energy": 0.4, "danceability": 0.5, "tempo": 120.0
        })
        
        # Valence difference should matter more (2x weight vs 1.5x)
        assert score_valence > score_energy


class TestPlaylist:
    """Tests for Playlist dataclass."""
    
    def test_create_empty_playlist(self):
        """Test creating an empty playlist."""
        playlist = Playlist(
            playlist_id="pl123",
            name="My Playlist",
            owner_id="user123"
        )
        
        assert playlist.playlist_id == "pl123"
        assert playlist.track_count == 0
        assert not playlist.is_public
    
    def test_add_track_to_playlist(self):
        """Test adding a track to playlist."""
        playlist = Playlist("pl123", "My Playlist", "user123")
        playlist.add_track("track1")
        
        assert playlist.track_count == 1
        assert "track1" in playlist.track_ids
    
    def test_add_duplicate_track_ignored(self):
        """Test that adding duplicate track is ignored."""
        playlist = Playlist("pl123", "My Playlist", "user123")
        playlist.add_track("track1")
        playlist.add_track("track1")
        
        assert playlist.track_count == 1
    
    def test_add_multiple_tracks(self):
        """Test adding multiple tracks."""
        playlist = Playlist("pl123", "My Playlist", "user123")
        playlist.add_track("track1")
        playlist.add_track("track2")
        playlist.add_track("track3")
        
        assert playlist.track_count == 3


class TestDefaultMoodPresets:
    """Tests for default mood preset constants."""
    
    def test_all_presets_exist(self):
        """Test that all expected mood presets are defined."""
        expected_moods = ["Happy", "Chill", "Focus", "Sad", "Hype", "Romantic"]
        
        for mood in expected_moods:
            assert mood in DEFAULT_MOOD_PRESETS
    
    def test_presets_have_valid_values(self):
        """Test that all presets have valid audio feature values."""
        for mood, preset in DEFAULT_MOOD_PRESETS.items():
            assert 0 <= preset.valence <= 1
            assert 0 <= preset.energy <= 1
            assert 0 <= preset.danceability <= 1
            assert 60 <= preset.tempo <= 200
            assert preset.name == mood


class TestSpotifyExceptions:
    """Tests for custom exception classes."""
    
    def test_spotify_error_basic(self):
        """Test creating basic SpotifyError."""
        error = SpotifyError("TEST_ERROR", "Test message")
        
        assert error.code == "TEST_ERROR"
        assert error.message == "Test message"
        assert str(error) == "[TEST_ERROR] Test message"
    
    def test_spotify_error_with_details(self):
        """Test SpotifyError with details dict."""
        error = SpotifyError(
            "TEST_ERROR",
            "Test message",
            details={"key": "value"}
        )
        
        assert error.details["key"] == "value"
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid credentials")
        
        assert error.code == "AUTH_FAILED"
        assert error.message == "Invalid credentials"
    
    def test_api_error_with_status_code(self):
        """Test APIError with status code."""
        error = APIError("Request failed", status_code=404)
        
        assert error.code == "API_ERROR"
        assert error.details["status_code"] == 404
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field name."""
        error = ValidationError("Invalid value", field="email")
        
        assert error.code == "VALIDATION_ERROR"
        assert error.details["field"] == "email"
