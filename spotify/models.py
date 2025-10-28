"""
📚 DATA MODELS FOR SPOTIFY MOOD RECOMMENDER

This module defines the core data structures used throughout the application.
Following the same patterns as src/models.py, we use dataclasses for clean,
immutable data structures with automatic equality checks and string representations.

DESIGN PRINCIPLES:
- Dataclasses: Auto-generate __init__, __repr__, __eq__ methods
- Type Hints: Explicit types for all fields
- Immutability: frozen=True prevents accidental modification
- Validation: Custom __post_init__ for data validation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass(frozen=True)
class MoodPreset:
    """
    Represents audio feature targets for a specific mood.
    
    📚 CONCEPT: Dataclasses with frozen=True create immutable objects.
    This prevents bugs from accidental modifications and makes the code
    more predictable and easier to test.
    
    AUDIO FEATURES EXPLAINED:
    - valence (0-1): Musical positivity (0=sad, 1=happy)
    - energy (0-1): Intensity and activity level
    - danceability (0-1): How suitable for dancing
    - tempo (BPM): Speed of the track in beats per minute
    
    Example:
        >>> happy = MoodPreset("Happy", 0.8, 0.7, 0.7, 120, "Upbeat and joyful")
        >>> print(happy.valence)
        0.8
    """
    name: str
    valence: float
    energy: float
    danceability: float
    tempo: int
    description: str
    
    def __post_init__(self):
        """Validate audio features are within acceptable ranges."""
        if not (0 <= self.valence <= 1):
            raise ValueError(f"Valence must be between 0 and 1, got {self.valence}")
        if not (0 <= self.energy <= 1):
            raise ValueError(f"Energy must be between 0 and 1, got {self.energy}")
        if not (0 <= self.danceability <= 1):
            raise ValueError(f"Danceability must be between 0 and 1, got {self.danceability}")
        if not (60 <= self.tempo <= 200):
            raise ValueError(f"Tempo must be between 60 and 200 BPM, got {self.tempo}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preset to dictionary format for API calls."""
        return {
            "valence": self.valence,
            "energy": self.energy,
            "danceability": self.danceability,
            "tempo": self.tempo
        }


@dataclass(frozen=True)
class UserProfile:
    """
    Represents a Spotify user's profile information.
    
    📚 DESIGN: Using Optional types for fields that might be missing.
    This makes our code more robust when dealing with incomplete API responses.
    
    Example:
        >>> profile = UserProfile("john_doe", "John", 150, "https://...", "spotify:user:john")
        >>> print(profile.display_name)
        'John'
    """
    user_id: str
    display_name: str
    followers: int = 0
    profile_image_url: Optional[str] = None
    spotify_url: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields are not empty."""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not self.display_name:
            raise ValueError("display_name cannot be empty")


@dataclass(frozen=True)
class Track:
    """
    Represents a Spotify track with essential information.
    
    📚 PATTERN: Separating data (Track) from behavior (SpotifyClient).
    This makes testing easier and follows Single Responsibility Principle.
    
    Example:
        >>> track = Track("123", "Song Name", ["Artist 1"], "Album", "https://...", "uri")
        >>> print(track.name)
        'Song Name'
    """
    track_id: str
    name: str
    artists: List[str]
    album_name: str
    spotify_url: str
    uri: str
    preview_url: Optional[str] = None
    album_image_url: Optional[str] = None
    
    def __post_init__(self):
        """Validate track has required fields."""
        if not self.track_id:
            raise ValueError("track_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.artists:
            raise ValueError("Track must have at least one artist")


@dataclass(frozen=True)
class AudioFeatures:
    """
    Represents Spotify audio analysis features for a track.
    
    📚 WHY SEPARATE CLASS: Audio features are optional and not all tracks
    have them available. Keeping them separate from Track makes the model
    more flexible and prevents None values in core track data.
    
    Example:
        >>> features = AudioFeatures("123", 0.8, 0.7, 0.6, 120)
        >>> print(features.valence)
        0.8
    """
    track_id: str
    valence: float
    energy: float
    danceability: float
    tempo: float
    
    def __post_init__(self):
        """Validate feature values are within expected ranges."""
        if not (0 <= self.valence <= 1):
            raise ValueError(f"Valence must be between 0 and 1, got {self.valence}")
        if not (0 <= self.energy <= 1):
            raise ValueError(f"Energy must be between 0 and 1, got {self.energy}")
        if not (0 <= self.danceability <= 1):
            raise ValueError(f"Danceability must be between 0 and 1, got {self.danceability}")
    
    def calculate_mood_score(self, target_features: Dict[str, float]) -> float:
        """
        Calculate similarity score between this track and target mood features.
        
        📚 ALGORITHM: Weighted Euclidean distance. Lower scores = better match.
        We weight valence higher (2x) because mood is primarily about emotional tone.
        
        Args:
            target_features: Dictionary with valence, energy, danceability, tempo
            
        Returns:
            Float score where lower is better match
            
        Example:
            >>> features = AudioFeatures("123", 0.8, 0.7, 0.6, 120)
            >>> target = {"valence": 0.9, "energy": 0.6, "danceability": 0.7, "tempo": 125}
            >>> score = features.calculate_mood_score(target)
            >>> print(f"Score: {score:.2f}")
            Score: 0.35
        """
        score = 0.0
        
        # Valence weighted most heavily (2x)
        score += abs(self.valence - target_features.get("valence", 0.5)) * 2.0
        
        # Energy and danceability weighted equally (1.5x)
        score += abs(self.energy - target_features.get("energy", 0.5)) * 1.5
        score += abs(self.danceability - target_features.get("danceability", 0.5)) * 1.5
        
        # Tempo difference normalized (divided by 100 to scale down)
        score += abs(self.tempo - target_features.get("tempo", 120)) / 100.0
        
        return score


@dataclass
class Playlist:
    """
    Represents a Spotify playlist (mutable to allow track additions).
    
    📚 DESIGN CHOICE: Not frozen because playlists can be modified after creation.
    This is an example of when mutability makes sense - the object represents
    a real-world entity that changes over time.
    
    Example:
        >>> playlist = Playlist("pl_123", "My Mood Playlist", "user_456")
        >>> playlist.add_track("track_789")
        >>> print(playlist.track_count)
        1
    """
    playlist_id: str
    name: str
    owner_id: str
    description: str = ""
    is_public: bool = False
    spotify_url: Optional[str] = None
    track_ids: List[str] = field(default_factory=list)
    
    def add_track(self, track_id: str) -> None:
        """Add a track to the playlist."""
        if track_id not in self.track_ids:
            self.track_ids.append(track_id)
    
    @property
    def track_count(self) -> int:
        """Get number of tracks in playlist."""
        return len(self.track_ids)


# 📚 CONSTANT: Default mood presets
# Defined at module level so they can be imported and used throughout the app
DEFAULT_MOOD_PRESETS: Dict[str, MoodPreset] = {
    "Happy": MoodPreset(
        name="Happy",
        valence=0.8,
        energy=0.7,
        danceability=0.7,
        tempo=120,
        description="Upbeat and joyful vibes"
    ),
    "Chill": MoodPreset(
        name="Chill",
        valence=0.5,
        energy=0.3,
        danceability=0.4,
        tempo=90,
        description="Relaxed and mellow tunes"
    ),
    "Focus": MoodPreset(
        name="Focus",
        valence=0.4,
        energy=0.4,
        danceability=0.3,
        tempo=100,
        description="Concentration-enhancing beats"
    ),
    "Sad": MoodPreset(
        name="Sad",
        valence=0.2,
        energy=0.3,
        danceability=0.3,
        tempo=80,
        description="Melancholic and introspective"
    ),
    "Hype": MoodPreset(
        name="Hype",
        valence=0.7,
        energy=0.9,
        danceability=0.8,
        tempo=140,
        description="High-energy pump-up tracks"
    ),
    "Romantic": MoodPreset(
        name="Romantic",
        valence=0.6,
        energy=0.4,
        danceability=0.5,
        tempo=95,
        description="Love songs and sweet melodies"
    )
}


class SpotifyError(Exception):
    """
    Base exception for Spotify-related errors.
    
    📚 PATTERN: Custom exceptions make error handling more specific and clear.
    Instead of catching generic Exception, we can catch SpotifyError and know
    exactly what went wrong.
    
    Example:
        >>> try:
        ...     raise SpotifyError("AUTH_FAILED", "Invalid API key")
        ... except SpotifyError as e:
        ...     print(f"Error {e.code}: {e.message}")
        Error AUTH_FAILED: Invalid API key
    """
    
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code}] {message}")


class AuthenticationError(SpotifyError):
    """Raised when Spotify authentication fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("AUTH_FAILED", message, details)


class APIError(SpotifyError):
    """Raised when Spotify API request fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if status_code:
            details["status_code"] = status_code
        super().__init__("API_ERROR", message, details)


class ValidationError(SpotifyError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__("VALIDATION_ERROR", message, details)
