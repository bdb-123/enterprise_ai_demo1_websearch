"""
📚 SPOTIFY RECOMMENDATION SERVICE

This module contains the business logic for mood-based music recommendations.
It orchestrates the SpotifyClient to provide high-level functionality.

DESIGN PRINCIPLES:
- Service Layer Pattern: Business logic separate from API calls and UI
- Single Responsibility: Each method does ONE thing well
- Dependency Injection: Client passed in, not created here (testability)
- Error Handling: Convert technical errors to user-friendly messages

ARCHITECTURE:
- Models: Data structures (models.py)
- Client: API communication (client.py)
- Service: Business logic (this file)
- UI: User interface (app.py)
"""

import logging
import random
from typing import List, Dict, Optional, Tuple

from spotify.models import (
    Track, AudioFeatures, MoodPreset, Playlist,
    APIError, ValidationError
)
from spotify.client import SpotifyClient

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for generating mood-based music recommendations.
    
    📚 SERVICE LAYER PATTERN: This class coordinates multiple operations
    to fulfill business requirements. It doesn't know about HTTP, UI, or
    low-level API details - just business logic.
    
    Example:
        >>> client = SpotifyClient()
        >>> service = RecommendationService(client)
        >>> tracks = service.get_mood_recommendations("Happy", limit=10)
    """
    
    def __init__(self, client: SpotifyClient):
        """
        Initialize service with Spotify client.
        
        📚 DEPENDENCY INJECTION: Client is passed in rather than created here.
        This makes testing easy - we can pass a mock client in tests.
        
        Args:
            client: Initialized SpotifyClient instance
        """
        self.client = client
        logger.info("RecommendationService initialized")
    
    def get_mood_recommendations(
        self,
        mood_preset: MoodPreset,
        limit: int = 10,
        use_user_library: bool = False,
        user_track_ids: Optional[List[str]] = None
    ) -> List[Track]:
        """
        Get track recommendations based on mood.
        
        📚 ALGORITHM: Two-phase approach
        1. If user has liked songs → analyze and match by audio features
        2. Else → search Spotify catalog with mood keywords
        
        Args:
            mood_preset: MoodPreset defining target audio features
            limit: Number of tracks to return
            use_user_library: Whether to use user's liked songs
            user_track_ids: Optional list of user's track IDs
            
        Returns:
            List of recommended Track objects
            
        Raises:
            ValidationError: If parameters are invalid
            APIError: If recommendation generation fails
        """
        if limit < 1 or limit > 50:
            raise ValidationError("Limit must be between 1 and 50", field="limit")
        
        logger.info(f"Getting {limit} recommendations for mood: {mood_preset.name}")
        
        # Strategy 1: Use user's library with audio feature matching
        if use_user_library and user_track_ids and len(user_track_ids) >= limit:
            try:
                tracks = self._recommend_from_library(
                    mood_preset,
                    user_track_ids,
                    limit
                )
                if tracks:
                    logger.info(f"Generated {len(tracks)} recommendations from user library")
                    return tracks
            except Exception as e:
                logger.warning(f"Failed to recommend from library: {e}")
                # Fall through to search-based approach
        
        # Strategy 2: Search Spotify catalog
        try:
            tracks = self._recommend_from_search(mood_preset, limit)
            logger.info(f"Generated {len(tracks)} recommendations from search")
            return tracks
        except Exception as e:
            logger.error(f"All recommendation strategies failed: {e}")
            raise APIError("Failed to generate recommendations")
    
    def _recommend_from_library(
        self,
        mood_preset: MoodPreset,
        track_ids: List[str],
        limit: int
    ) -> List[Track]:
        """
        Recommend tracks from user's library by matching audio features.
        
        📚 ALGORITHM:
        1. Sample tracks from library (for performance)
        2. Get audio features for sample
        3. Calculate mood match score for each track
        4. Sort by score (best matches first)
        5. Return top N tracks
        
        Args:
            mood_preset: Target mood features
            track_ids: User's track IDs
            limit: Number of recommendations
            
        Returns:
            List of recommended tracks
        """
        logger.debug(f"Recommending from library of {len(track_ids)} tracks")
        
        # Sample tracks for performance (max 100 to analyze)
        sample_size = min(100, len(track_ids))
        sampled_ids = random.sample(track_ids, sample_size)
        
        # Get audio features in batches
        audio_features = self._get_audio_features_safe(sampled_ids)
        
        if not audio_features:
            logger.warning("No audio features available from library")
            return []
        
        # Score and sort tracks by mood match
        scored_tracks = self._score_tracks_by_mood(
            audio_features,
            mood_preset.to_dict()
        )
        
        if not scored_tracks:
            return []
        
        # Get best matching track IDs
        best_track_ids = [track_id for track_id, score in scored_tracks[:limit]]
        
        # Fetch full track details
        tracks = self._get_tracks_in_batches(best_track_ids)
        
        logger.info(f"Matched {len(tracks)} tracks from library to mood: {mood_preset.name}")
        return tracks
    
    def _get_audio_features_safe(self, track_ids: List[str]) -> List[AudioFeatures]:
        """
        Safely get audio features with error handling and batching.
        
        📚 ROBUSTNESS: Even if some batches fail, we return what we can.
        This prevents one bad track from failing the entire request.
        
        Args:
            track_ids: List of track IDs
            
        Returns:
            List of AudioFeatures (may be incomplete)
        """
        features = []
        
        # Process in batches of 100 (API limit)
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            
            try:
                batch_features = self.client.get_audio_features(batch)
                features.extend(batch_features)
            except Exception as e:
                logger.warning(f"Failed to get audio features for batch: {e}")
                # Try individual tracks as fallback
                for track_id in batch:
                    try:
                        track_features = self.client.get_audio_features([track_id])
                        features.extend(track_features)
                    except Exception:
                        pass  # Skip tracks that fail
        
        return features
    
    def _score_tracks_by_mood(
        self,
        audio_features: List[AudioFeatures],
        target_features: Dict[str, float]
    ) -> List[Tuple[str, float]]:
        """
        Score tracks by how well they match target mood features.
        
        📚 SCORING ALGORITHM: Weighted Euclidean distance
        - Valence (positivity) weighted highest
        - Energy and danceability weighted equally
        - Tempo difference normalized
        
        Lower scores = better match
        
        Args:
            audio_features: List of track audio features
            target_features: Target mood feature values
            
        Returns:
            List of (track_id, score) tuples sorted by score (ascending)
        """
        scored = []
        
        for features in audio_features:
            try:
                score = features.calculate_mood_score(target_features)
                scored.append((features.track_id, score))
            except Exception as e:
                logger.warning(f"Failed to score track {features.track_id}: {e}")
        
        # Sort by score (ascending = best matches first)
        scored.sort(key=lambda x: x[1])
        
        logger.debug(f"Scored {len(scored)} tracks for mood matching")
        return scored
    
    def _get_tracks_in_batches(self, track_ids: List[str]) -> List[Track]:
        """
        Get track details in batches of 50 (API limit).
        
        Args:
            track_ids: List of track IDs
            
        Returns:
            List of Track objects
        """
        tracks = []
        
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i+50]
            try:
                batch_tracks = self.client.get_tracks(batch)
                tracks.extend(batch_tracks)
            except Exception as e:
                logger.warning(f"Failed to get track batch: {e}")
        
        return tracks
    
    def _recommend_from_search(
        self,
        mood_preset: MoodPreset,
        limit: int
    ) -> List[Track]:
        """
        Recommend tracks by searching Spotify catalog.
        
        📚 FALLBACK STRATEGY: Multiple search attempts with increasingly
        broader criteria until we find enough tracks.
        
        Args:
            mood_preset: Target mood
            limit: Number of recommendations
            
        Returns:
            List of recommended tracks
        """
        logger.debug(f"Searching catalog for mood: {mood_preset.name}")
        
        # Generate search queries with different strategies
        queries = self._generate_search_queries(mood_preset)
        
        # Try each query until we get enough results
        for query in queries:
            try:
                tracks = self.client.search_tracks(
                    query=query,
                    limit=min(limit * 3, 50)  # Get extra for filtering
                )
                
                if len(tracks) >= limit:
                    logger.info(f"Found {len(tracks)} tracks with query: {query}")
                    return tracks[:limit]
                    
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                continue
        
        # If we get here, no search worked
        logger.error("All search strategies failed")
        return []
    
    def _generate_search_queries(self, mood_preset: MoodPreset) -> List[str]:
        """
        Generate multiple search queries for a mood.
        
        📚 PROGRESSIVE FALLBACK: Start specific, get broader.
        Each query is more likely to return results than the last.
        
        Args:
            mood_preset: Target mood
            
        Returns:
            List of search query strings (most specific first)
        """
        # Mood-specific keywords
        mood_keywords = {
            "Happy": ["happy", "upbeat", "cheerful", "positive", "joyful"],
            "Chill": ["chill", "relaxed", "mellow", "ambient", "calm"],
            "Focus": ["focus", "study", "concentration", "ambient", "instrumental"],
            "Sad": ["sad", "melancholy", "emotional", "ballad", "heartbreak"],
            "Hype": ["hype", "energetic", "pump", "party", "workout"],
            "Romantic": ["romantic", "love", "beautiful", "emotional", "sweet"]
        }
        
        keywords = mood_keywords.get(mood_preset.name, ["pop"])
        
        # Year ranges based on energy level
        if mood_preset.energy > 0.7:
            year_filter = " year:2020-2025"
        elif mood_preset.energy > 0.4:
            year_filter = " year:2015-2025"
        else:
            year_filter = " year:2010-2025"
        
        queries = []
        
        # Strategy 1: Primary keyword + year filter
        queries.append(f"{keywords[0]}{year_filter}")
        
        # Strategy 2: Primary keyword without year filter
        queries.append(keywords[0])
        
        # Strategy 3: Secondary keyword
        if len(keywords) > 1:
            queries.append(keywords[1])
        
        # Strategy 4: Generic mood search
        queries.append(mood_preset.name.lower())
        
        # Strategy 5: Last resort - popular tracks
        queries.append("top hits 2024")
        
        return queries
    
    def create_mood_playlist(
        self,
        user_id: str,
        mood_name: str,
        tracks: List[Track]
    ) -> Playlist:
        """
        Create a playlist from recommended tracks.
        
        Args:
            user_id: Spotify user ID
            mood_name: Name of the mood
            tracks: List of tracks to add
            
        Returns:
            Created Playlist object
            
        Raises:
            ValidationError: If tracks list is empty
            APIError: If playlist creation fails
        """
        if not tracks:
            raise ValidationError("Cannot create playlist with no tracks")
        
        playlist_name = f"Mood2Music – {mood_name}"
        description = f"Tracks recommended by Mood2Music for {mood_name} mood"
        
        logger.info(f"Creating playlist: {playlist_name}")
        
        # Create the playlist
        playlist = self.client.create_playlist(
            user_id=user_id,
            name=playlist_name,
            description=description,
            is_public=False
        )
        
        # Add tracks in batches of 100
        track_ids = [track.track_id for track in tracks]
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            self.client.add_tracks_to_playlist(playlist.playlist_id, batch)
            playlist.track_ids.extend(batch)
        
        logger.info(f"Created playlist with {len(tracks)} tracks")
        return playlist
    
    def get_available_genres(self) -> List[str]:
        """
        Get list of available Spotify genre seeds.
        
        📚 CACHED DATA: Since genre list rarely changes, we use
        a hardcoded list rather than making an API call every time.
        
        Returns:
            List of genre strings
        """
        return [
            "acoustic", "afrobeat", "alt-rock", "alternative", "ambient",
            "anime", "black-metal", "bluegrass", "blues", "bossanova",
            "brazil", "breakbeat", "british", "cantopop", "chicago-house",
            "children", "chill", "classical", "club", "comedy", "country",
            "dance", "dancehall", "death-metal", "deep-house", "detroit-techno",
            "disco", "disney", "drum-and-bass", "dub", "dubstep", "edm",
            "electro", "electronic", "emo", "folk", "forro", "french",
            "funk", "garage", "german", "gospel", "goth", "grindcore",
            "groove", "grunge", "guitar", "happy", "hard-rock", "hardcore",
            "hardstyle", "heavy-metal", "hip-hop", "holidays", "honky-tonk",
            "house", "idm", "indian", "indie", "indie-pop", "industrial",
            "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz",
            "k-pop", "kids", "latin", "latino", "malay", "mandopop",
            "metal", "metal-misc", "metalcore", "minimal-techno", "movies",
            "mpb", "new-age", "new-release", "opera", "pagode", "party",
            "philippines-opm", "piano", "pop", "pop-film", "post-dubstep",
            "power-pop", "progressive-house", "psych-rock", "punk",
            "punk-rock", "r-n-b", "rainy-day", "reggae", "reggaeton",
            "road-trip", "rock", "rock-n-roll", "rockabilly", "romance",
            "sad", "salsa", "samba", "sertanejo", "show-tunes",
            "singer-songwriter", "ska", "sleep", "songwriter", "soul",
            "soundtracks", "spanish", "study", "summer", "swedish",
            "synth-pop", "tango", "techno", "trance", "trip-hop",
            "turkish", "work-out", "world-music"
        ]
