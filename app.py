"""
Spotify Mood-Based Track Recommender
A Streamlit app that recommends tracks based on selected mood and customizable audio features.
Includes an AI chatbot for natural language music requests.
"""

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Spotify Mood Recommender",
    page_icon="🎵",
    layout="wide"
)

# Mood presets with audio feature mappings
MOOD_PRESETS = {
    "Happy": {
        "valence": 0.8,
        "energy": 0.7,
        "danceability": 0.7,
        "tempo": 120,
        "description": "Upbeat and joyful vibes"
    },
    "Chill": {
        "valence": 0.5,
        "energy": 0.3,
        "danceability": 0.4,
        "tempo": 90,
        "description": "Relaxed and mellow tunes"
    },
    "Focus": {
        "valence": 0.4,
        "energy": 0.4,
        "danceability": 0.3,
        "tempo": 100,
        "description": "Concentration-enhancing beats"
    },
    "Sad": {
        "valence": 0.2,
        "energy": 0.3,
        "danceability": 0.3,
        "tempo": 80,
        "description": "Melancholic and introspective"
    },
    "Hype": {
        "valence": 0.7,
        "energy": 0.9,
        "danceability": 0.8,
        "tempo": 140,
        "description": "High-energy pump-up tracks"
    },
    "Romantic": {
        "valence": 0.6,
        "energy": 0.4,
        "danceability": 0.5,
        "tempo": 95,
        "description": "Love songs and sweet melodies"
    }
}


# Chatbot mood keywords for natural language processing
CHATBOT_MOOD_KEYWORDS = {
    "happy": ["happy", "joyful", "cheerful", "upbeat", "positive", "excited", "fun", "party"],
    "chill": ["chill", "relax", "calm", "mellow", "laid back", "easy", "peaceful", "ambient"],
    "focus": ["focus", "study", "concentrate", "work", "productivity", "coding", "reading"],
    "sad": ["sad", "melancholy", "emotional", "cry", "heartbreak", "depressed", "down", "blue"],
    "hype": ["hype", "energetic", "workout", "gym", "pump", "intense", "motivate", "power"],
    "romantic": ["romantic", "love", "date", "valentine", "couple", "intimate", "sensual"]
}

# Activity to mood mapping
ACTIVITY_MOOD_MAP = {
    "workout": "Hype",
    "gym": "Hype",
    "exercise": "Hype",
    "running": "Hype",
    "study": "Focus",
    "work": "Focus",
    "coding": "Focus",
    "reading": "Focus",
    "sleep": "Chill",
    "meditate": "Chill",
    "yoga": "Chill",
    "party": "Happy",
    "dance": "Happy",
    "celebrate": "Happy",
    "date": "Romantic",
    "dinner": "Romantic",
}


def parse_mood_from_text(user_input):
    """
    Extract mood and preferences from natural language input.
    Returns: (mood_name, mood_features, explanation)
    """
    user_input_lower = user_input.lower()
    
    # Check for activity keywords first
    for activity, mood in ACTIVITY_MOOD_MAP.items():
        if activity in user_input_lower:
            features = MOOD_PRESETS[mood].copy()
            return mood, features, f"Perfect for {activity}! Setting mood to {mood}."
    
    # Check for direct mood keywords
    mood_scores = {}
    for mood_name, keywords in CHATBOT_MOOD_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in user_input_lower)
        if score > 0:
            mood_scores[mood_name] = score
    
    if mood_scores:
        # Get the mood with highest keyword match
        best_mood = max(mood_scores, key=mood_scores.get)
        mood_name = best_mood.capitalize()
        features = MOOD_PRESETS[mood_name].copy()
        return mood_name, features, f"Detected {mood_name} mood from your request!"
    
    # Check for energy level adjustments
    if any(word in user_input_lower for word in ["more energy", "energetic", "faster", "upbeat"]):
        features = MOOD_PRESETS["Hype"].copy()
        return "Hype", features, "You want high energy! Setting to Hype mode."
    
    if any(word in user_input_lower for word in ["slower", "calmer", "quieter", "softer"]):
        features = MOOD_PRESETS["Chill"].copy()
        return "Chill", features, "You want something calmer! Setting to Chill mode."
    
    # Default to Happy if no clear mood detected
    return "Happy", MOOD_PRESETS["Happy"].copy(), "No specific mood detected, showing upbeat tracks!"


def extract_artist_from_text(user_input):
    """
    Try to extract artist name from user input.
    Returns artist name if found, None otherwise.
    """
    user_input_lower = user_input.lower()
    
    # Common patterns for artist requests
    patterns = [
        "songs by ",
        "music by ",
        "tracks by ",
        "artist ",
        "listen to ",
        "play ",
        "from ",
    ]
    
    for pattern in patterns:
        if pattern in user_input_lower:
            # Extract text after the pattern
            start_idx = user_input_lower.index(pattern) + len(pattern)
            remaining = user_input[start_idx:].strip()
            
            # Take until punctuation or "songs"/"music"/"tracks"
            artist = remaining.split()[0] if remaining else None
            
            # Handle multi-word artist names (take up to 3 words or until "songs"/"music")
            words = remaining.split()
            if len(words) > 1:
                # Stop at common keywords
                stop_words = ["songs", "music", "tracks", "please", "that", "are", "is"]
                artist_words = []
                for word in words[:4]:  # Max 4 words for artist name
                    if word.lower() in stop_words:
                        break
                    artist_words.append(word)
                
                if artist_words:
                    artist = " ".join(artist_words)
            
            return artist.strip() if artist else None
    
    return None


def generate_chatbot_response(user_input, tracks, mood_name):
    """Generate a friendly chatbot response with track recommendations"""
    responses = {
        "Happy": [
            f"🎉 Found {len(tracks)} upbeat tracks to boost your mood!",
            f"☀️ Here are {len(tracks)} cheerful songs from your library!",
            f"😊 {len(tracks)} happy vibes coming right up!"
        ],
        "Chill": [
            f"😌 Found {len(tracks)} relaxing tracks for you",
            f"🌙 Here are {len(tracks)} chill songs to help you unwind",
            f"☁️ {len(tracks)} mellow tracks from your collection"
        ],
        "Focus": [
            f"🎯 Found {len(tracks)} tracks to boost your concentration",
            f"📚 Here are {len(tracks)} focus-enhancing songs",
            f"💡 {len(tracks)} productivity tracks ready!"
        ],
        "Sad": [
            f"💙 Found {len(tracks)} songs that match your mood",
            f"🌧️ Here are {len(tracks)} emotional tracks",
            f"🎭 {len(tracks)} songs to help you process those feelings"
        ],
        "Hype": [
            f"🔥 Found {len(tracks)} high-energy bangers!",
            f"⚡ Here are {len(tracks)} tracks to get you pumped!",
            f"💪 {len(tracks)} intense songs to fuel your energy!"
        ],
        "Romantic": [
            f"❤️ Found {len(tracks)} romantic tracks for you",
            f"💕 Here are {len(tracks)} love songs from your library",
            f"🌹 {len(tracks)} beautiful tracks for your special moment"
        ]
    }
    
    import random
    return random.choice(responses.get(mood_name, [f"Found {len(tracks)} tracks for you!"]))


@st.cache_resource
def get_spotify_client():
    """Initialize and cache Spotify client with OAuth support"""
    try:
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
        
        if not client_id or not client_secret:
            st.error("⚠️ Spotify credentials not found!")
            st.info("Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables.")
            st.stop()
        
        if not redirect_uri:
            st.error("Missing SPOTIPY_REDIRECT_URI. Set it in Streamlit Secrets.")
            st.stop()
        
        # Validate redirect URI format
        if not redirect_uri.startswith(("http://", "https://")):
            st.error(f"❌ Invalid SPOTIPY_REDIRECT_URI: {redirect_uri}")
            st.info("Redirect URI must start with http:// or https://")
            st.stop()
        
        # Use OAuth for user authentication (allows access to liked songs, top tracks, and playlist creation)
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read user-top-read playlist-modify-private",
            cache_path=".cache_streamlit",
            show_dialog=True,
            open_browser=False  # Don't try to open browser in Streamlit Cloud
        )
        
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp, auth_manager
    except Exception as e:
        st.error(f"Error initializing Spotify client: {e}")
        st.stop()


def get_spotify_client_credentials_only():
    """Fallback: Initialize Spotify client with Client Credentials (no user auth)"""
    try:
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            st.error("⚠️ Spotify credentials not found!")
            st.stop()
        
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp
    except Exception as e:
        st.error(f"Error initializing Spotify client: {e}")
        st.stop()


def get_user_liked_track_ids(sp, max_ids=300):
    """Get up to 300 of the user's saved (Liked) tracks with strict validation"""
    try:
        items = []
        results = sp.current_user_saved_tracks(limit=50)
        items += results.get("items", [])
        
        while results.get("next") and len(items) < max_ids:
            results = sp.next(results)
            items += results.get("items", [])
        
        # Keep only real Spotify track IDs with strict validation
        ids = []
        for it in items:
            t = it.get("track")
            if not t: 
                continue
            if t.get("type") != "track":
                continue
            if t.get("is_local"):
                continue
            tid = t.get("id")
            if tid:
                ids.append(tid)
        
        return ids
    except Exception as e:
        st.warning(f"Could not fetch liked songs: {e}")
        return []


def safe_audio_features(sp, track_ids):
    """Safely get audio features with fallback for individual tracks"""
    feats = []
    # Chunk to 100 IDs at a time
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i+100]
        try:
            res = sp.audio_features(batch) or []
            feats.extend([r for r in res if r])
        except Exception:
            # Fallback: try each ID individually
            for tid in batch:
                try:
                    r = sp.audio_features([tid])
                    if r and r[0]:
                        feats.append(r[0])
                except Exception:
                    pass
    return feats


def get_user_profile(sp):
    """Get the current user's Spotify profile information"""
    try:
        user = sp.current_user()
        return {
            "display_name": user.get("display_name", "Spotify User"),
            "id": user.get("id", ""),
            "profile_image": user.get("images", [{}])[0].get("url", "") if user.get("images") else "",
            "followers": user.get("followers", {}).get("total", 0),
            "url": user.get("external_urls", {}).get("spotify", "")
        }
    except Exception as e:
        st.warning(f"Could not fetch user profile: {e}")
        return None


def get_user_top_tracks(sp, limit=20):
    """Get user's top tracks as fallback seed source"""
    try:
        results = sp.current_user_top_tracks(limit=limit, time_range='medium_term')
        track_ids = [
            item["id"]
            for item in results.get("items", [])
            if item and item.get("id") and not item.get("is_local", False)
        ]
        return track_ids
    except Exception as e:
        # Likely missing user-top-read scope
        return []


def get_top_track_ids(sp, limit=50):
    """Get user's top track IDs (simplified version for seeding)"""
    try:
        res = sp.current_user_top_tracks(limit=min(limit, 50), time_range="medium_term")
        return [t["id"] for t in res.get("items", []) if t and t.get("id")]
    except Exception as e:
        return []


def filter_liked_songs_by_mood(sp, track_ids, mood_features, limit=10):
    """Filter user's liked songs based on mood features"""
    try:
        if not track_ids:
            st.warning("No track IDs provided for filtering.")
            return []
        
        # Get audio features safely with fallback handling
        audio_features_list = safe_audio_features(sp, track_ids)
        
        # Guard against empty results
        if not audio_features_list:
            st.warning("No usable audio features from your Liked Songs. Showing search-based results instead.")
            return []
        
        # Score each track based on how well it matches the mood
        scored_tracks = []
        for features in audio_features_list:
            if not features:
                continue
            
            # Calculate similarity score (lower is better)
            score = 0
            score += abs(features.get("valence", 0.5) - mood_features["valence"]) * 2
            score += abs(features.get("energy", 0.5) - mood_features["energy"]) * 1.5
            score += abs(features.get("danceability", 0.5) - mood_features["danceability"]) * 1.5
            score += abs(features.get("tempo", 120) - mood_features["tempo"]) / 100
            
            scored_tracks.append((features["id"], score))
        
        if not scored_tracks:
            st.warning("Could not score any tracks. Falling back to search.")
            return []
        
        # Sort by score (best matches first) and get top tracks
        scored_tracks.sort(key=lambda x: x[1])
        best_track_ids = [track_id for track_id, _ in scored_tracks[:limit]]
        
        # Get full track details
        tracks = []
        for i in range(0, len(best_track_ids), 50):
            batch = best_track_ids[i:i+50]
            try:
                track_results = sp.tracks(batch)
                if track_results and track_results.get("tracks"):
                    tracks.extend(track_results["tracks"])
            except Exception as e:
                st.warning(f"Error fetching track details: {e}")
        
        return tracks[:limit]
    
    except Exception as e:
        st.warning(f"Error filtering liked songs: {e}")
        return []


@st.cache_data(ttl=3600)
def get_available_genres(_sp):
    """Get list of available Spotify genres (cached for 1 hour)"""
    # Use a hardcoded list of common genres since the API endpoint may have issues
    return [
        "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime",
        "black-metal", "bluegrass", "blues", "bossanova", "brazil", "breakbeat",
        "british", "cantopop", "chicago-house", "children", "chill", "classical",
        "club", "comedy", "country", "dance", "dancehall", "death-metal", "deep-house",
        "detroit-techno", "disco", "disney", "drum-and-bass", "dub", "dubstep",
        "edm", "electro", "electronic", "emo", "folk", "forro", "french", "funk",
        "garage", "german", "gospel", "goth", "grindcore", "groove", "grunge",
        "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal",
        "hip-hop", "holidays", "honky-tonk", "house", "idm", "indian", "indie",
        "indie-pop", "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock",
        "jazz", "k-pop", "kids", "latin", "latino", "malay", "mandopop", "metal",
        "metal-misc", "metalcore", "minimal-techno", "movies", "mpb", "new-age",
        "new-release", "opera", "pagode", "party", "philippines-opm", "piano",
        "pop", "pop-film", "post-dubstep", "power-pop", "progressive-house",
        "psych-rock", "punk", "punk-rock", "r-n-b", "rainy-day", "reggae",
        "reggaeton", "road-trip", "rock", "rock-n-roll", "rockabilly", "romance",
        "sad", "salsa", "samba", "sertanejo", "show-tunes", "singer-songwriter",
        "ska", "sleep", "songwriter", "soul", "soundtracks", "spanish", "study",
        "summer", "swedish", "synth-pop", "tango", "techno", "trance", "trip-hop",
        "turkish", "work-out", "world-music"
    ]


def normalize_genres(user_genres, available_genres):
    """Normalize and validate user-selected genres against Spotify's official list"""
    # Genre alias mappings for common variations
    genre_aliases = {
        "indie": "indie-pop",
        "rnb": "r-n-b",
        "r&b": "r-n-b",
        "r-and-b": "r-n-b",
        "hiphop": "hip-hop",
        "hip hop": "hip-hop"
    }
    
    validated_genres = []
    for genre in user_genres:
        genre_lower = genre.lower().strip()
        
        # Check if genre exists as-is
        if genre_lower in available_genres:
            validated_genres.append(genre_lower)
        # Check if there's an alias mapping
        elif genre_lower in genre_aliases and genre_aliases[genre_lower] in available_genres:
            validated_genres.append(genre_aliases[genre_lower])
    
    # Return up to 5 valid genres, or default to ["pop"]
    return validated_genres[:5] if validated_genres else ["pop"]


def get_mood_specific_genres(selected_mood):
    """Get genre seeds that match the selected mood"""
    mood_genre_map = {
        "Happy": ["pop", "dance", "party", "funk", "disco"],
        "Chill": ["ambient", "chill", "indie", "acoustic", "lo-fi"],
        "Focus": ["ambient", "classical", "piano", "study", "minimal-techno"],
        "Sad": ["acoustic", "singer-songwriter", "indie", "sad", "emo"],
        "Hype": ["edm", "hip-hop", "rock", "hardstyle", "dubstep"],
        "Romantic": ["romance", "r-n-b", "soul", "indie-pop", "pop"]
    }
    return mood_genre_map.get(selected_mood, ["pop", "indie"])


def get_mood_search_query(selected_mood, mood_features):
    """Generate a search query based on mood and features"""
    mood_keywords = {
        "Happy": "happy upbeat cheerful positive",
        "Chill": "chill relaxed mellow ambient",
        "Focus": "focus study concentration ambient",
        "Sad": "sad melancholy emotional ballad",
        "Hype": "hype energetic pump party workout",
        "Romantic": "romantic love beautiful emotional"
    }
    return mood_keywords.get(selected_mood, "pop")


def score_track_match(track_features, target_features):
    """
    Calculate how well a track's audio features match the target mood.
    Returns a score where lower is better (0 = perfect match).
    """
    if not track_features:
        return float('inf')  # Worst possible score for missing features
    
    score = 0.0
    
    # Valence (musical positivity) - weighted heavily
    score += abs(track_features.get("valence", 0.5) - target_features["valence"]) * 2.5
    
    # Energy - weighted heavily
    score += abs(track_features.get("energy", 0.5) - target_features["energy"]) * 2.0
    
    # Danceability - moderate weight
    score += abs(track_features.get("danceability", 0.5) - target_features["danceability"]) * 1.5
    
    # Tempo - normalized to 0-1 scale, lower weight
    tempo_diff = abs(track_features.get("tempo", 120) - target_features["tempo"]) / 200
    score += tempo_diff * 1.0
    
    return score


def filter_tracks_by_mood(sp, tracks, mood_features, limit=10):
    """
    Filter and rank tracks based on how well they match the mood's audio features.
    
    Args:
        sp: Spotify client
        tracks: List of track objects from search
        mood_features: Target audio features (valence, energy, danceability, tempo)
        limit: Maximum number of tracks to return
    
    Returns:
        List of best-matching tracks, sorted by match quality
    """
    if not tracks:
        return []
    
    # Get track IDs
    track_ids = [track["id"] for track in tracks if track and track.get("id")]
    
    if not track_ids:
        return []
    
    try:
        # Get audio features in batches of 100
        all_features = []
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            try:
                features_batch = sp.audio_features(batch)
                all_features.extend([f for f in features_batch if f])
            except:
                # Skip failed batches
                pass
        
        if not all_features:
            # If we can't get audio features, return original tracks
            return tracks[:limit]
        
        # Score each track
        scored_tracks = []
        features_by_id = {f["id"]: f for f in all_features if f and f.get("id")}
        
        for track in tracks:
            if not track or not track.get("id"):
                continue
            
            track_id = track["id"]
            if track_id in features_by_id:
                features = features_by_id[track_id]
                score = score_track_match(features, mood_features)
                scored_tracks.append((track, score))
        
        if not scored_tracks:
            return tracks[:limit]
        
        # Sort by score (lower is better) and return top matches
        scored_tracks.sort(key=lambda x: x[1])
        return [track for track, score in scored_tracks[:limit]]
        
    except Exception as e:
        # If anything fails, return original tracks
        st.warning(f"Could not filter by audio features: {e}")
        return tracks[:limit]


def get_recommendations(sp, mood_features, selected_mood="Happy", limit=10, use_liked_songs=False, liked_track_ids=None):
    """Get track recommendations using liked songs with improved seed selection"""
    try:
        # If user is logged in and has liked songs, show them songs FROM their library!
        if use_liked_songs and liked_track_ids and len(liked_track_ids) >= limit:
            import random
            
            st.info(f"🎵 Analyzing your {len(liked_track_ids)} liked songs to match {selected_mood} mood...")
            
            # Try to get audio features and filter by mood
            try:
                # Get a larger sample to filter from
                sample_size = min(100, len(liked_track_ids))
                sample_ids = random.sample(liked_track_ids, sample_size)
                
                # Get audio features in batches
                audio_features_list = []
                for i in range(0, len(sample_ids), 100):
                    batch = sample_ids[i:i+100]
                    try:
                        features_batch = sp.audio_features(batch)
                        audio_features_list.extend([f for f in features_batch if f])
                    except:
                        # If audio features fail, skip this batch
                        pass
                
                if len(audio_features_list) >= limit:
                    # Score each track based on mood match
                    scored_tracks = []
                    for features in audio_features_list:
                        if not features or not features.get("id"):
                            continue
                        
                        # Calculate similarity score (lower is better)
                        score = 0
                        score += abs(features.get("valence", 0.5) - mood_features["valence"]) * 2
                        score += abs(features.get("energy", 0.5) - mood_features["energy"]) * 1.5
                        score += abs(features.get("danceability", 0.5) - mood_features["danceability"]) * 1.2
                        
                        scored_tracks.append((features["id"], score))
                    
                    # Sort by score and get the best matches
                    scored_tracks.sort(key=lambda x: x[1])
                    best_track_ids = [track_id for track_id, score in scored_tracks[:limit]]
                    
                    # Get full track details
                    tracks = []
                    for i in range(0, len(best_track_ids), 50):
                        batch = best_track_ids[i:i+50]
                        results = sp.tracks(batch)
                        tracks.extend(results.get("tracks", []))
                    
                    if tracks:
                        st.success(f"✅ Found {len(tracks)} songs from YOUR library that match {selected_mood} mood!")
                        return tracks[:limit]
                
            except Exception as e:
                # If filtering fails, fall back to random selection
                st.info(f"Could not analyze mood features, showing random picks from your library...")
            
            # Fallback: just show random songs from their library
            selected_ids = random.sample(liked_track_ids, min(limit, len(liked_track_ids)))
            
            # Get track details
            try:
                tracks = []
                for i in range(0, len(selected_ids), 50):
                    batch = selected_ids[i:i+50]
                    results = sp.tracks(batch)
                    tracks.extend(results.get("tracks", []))
                
                if tracks:
                    st.success(f"✅ Found {len(tracks)} random songs from YOUR liked songs!")
                    return tracks[:limit]
            except Exception as e:
                st.warning(f"Could not fetch track details: {e}")
        
        # Fallback to search-based approach
        # Get official Spotify genre list
        available_genres = get_available_genres(sp)
        
        # Use mood-specific genre seeds for better matching
        mood_genres = get_mood_specific_genres(selected_mood)
        seed_genres = normalize_genres(mood_genres, available_genres)
        
        # Build search query based on mood
        search_query = get_mood_search_query(selected_mood, mood_features)
        
        # Determine year range based on energy (higher energy = more recent)
        # Make year range broader to increase results
        if mood_features["energy"] > 0.7:
            year_filter = " year:2018-2025"
        elif mood_features["energy"] > 0.4:
            year_filter = " year:2010-2025"
        else:
            year_filter = " year:2000-2025"
        
        tracks = []
        
        # Attempt 1: Search with mood query and year filter
        try:
            results = sp.search(
                q=search_query + year_filter,
                limit=50,  # Get more results to filter by audio features
                type='track',
                market='US'
            )
            raw_tracks = results.get('tracks', {}).get('items', [])
            if raw_tracks:
                # Filter by audio features to ensure mood match
                tracks = filter_tracks_by_mood(sp, raw_tracks, mood_features, limit)
        except Exception as e:
            st.warning(f"Initial search failed: {e}")
        
        # Attempt 2: If no tracks, try without year filter (broader search)
        if not tracks:
            st.info("🔄 Expanding search criteria...")
            try:
                results = sp.search(
                    q=search_query,
                    limit=50,
                    type='track',
                    market='US'
                )
                raw_tracks = results.get('tracks', {}).get('items', [])
                if raw_tracks:
                    tracks = filter_tracks_by_mood(sp, raw_tracks, mood_features, limit)
            except Exception as e:
                st.warning(f"Broader search failed: {e}")
        
        # Attempt 3: If still no tracks, use generic mood keyword only
        if not tracks:
            st.info("🔄 Using broader mood search...")
            try:
                generic_query = selected_mood.lower()
                results = sp.search(
                    q=generic_query,
                    limit=50,
                    type='track',
                    market='US'
                )
                raw_tracks = results.get('tracks', {}).get('items', [])
                if raw_tracks:
                    tracks = filter_tracks_by_mood(sp, raw_tracks, mood_features, limit)
            except Exception as e:
                st.warning(f"Generic search failed: {e}")
        
        # Attempt 4: Last resort - search with genre + mood
        if not tracks:
            st.info("🔄 Trying genre-based search...")
            try:
                # Use first mood-specific genre
                genre_query = f"genre:{seed_genres[0]}" if seed_genres else "pop"
                results = sp.search(
                    q=f"{genre_query} {search_query}",
                    limit=50,
                    type='track',
                    market='US'
                )
                raw_tracks = results.get('tracks', {}).get('items', [])
                if raw_tracks:
                    tracks = filter_tracks_by_mood(sp, raw_tracks, mood_features, limit)
            except Exception as e:
                st.warning(f"Genre search failed: {e}")
        
        # Attempt 5: Absolute last resort - just use mood keyword search without filtering
        if not tracks:
            st.info("🔄 Finding popular tracks as fallback...")
            try:
                results = sp.search(
                    q=search_query,
                    limit=limit * 2,
                    type='track',
                    market='US'
                )
                raw_tracks = results.get('tracks', {}).get('items', [])
                if raw_tracks:
                    st.warning("⚠️ Showing unfiltered results (audio feature validation unavailable).")
                    tracks = raw_tracks[:limit]
            except Exception as e:
                st.error(f"All search attempts failed: {e}")
        
        if not tracks:
            st.error("❌ Unable to find any tracks. Please try again later or adjust your settings.")
            return []
        
        # Tracks are already filtered and limited by filter_tracks_by_mood
        st.success(f"✨ Found {len(tracks)} tracks matching {selected_mood} mood characteristics!")
        return tracks
        
    except spotipy.exceptions.SpotifyException as e:
        st.error(f"❌ Spotify API error ({e.http_status}): {e.msg}")
        # Last ditch effort - return empty but don't crash
        return []
    except Exception as e:
        st.error(f"❌ Unexpected error getting recommendations: {e}")
        return []


def create_playlist_from_tracks(sp, user_id, mood, tracks):
    """Create a private playlist with the recommended tracks"""
    try:
        # Create playlist name
        playlist_name = f"Mood2Music – {mood}"
        
        # Create the playlist
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=f"Tracks recommended by Mood2Music for {mood} mood"
        )
        
        # Get track URIs
        track_uris = [track["uri"] for track in tracks if track.get("uri")]
        
        # Add tracks to playlist (Spotify allows up to 100 at once)
        if track_uris:
            sp.playlist_add_items(playlist["id"], track_uris)
        
        return playlist
    except Exception as e:
        st.error(f"Failed to create playlist: {e}")
        return None


def display_track(track, index):
    """Display a single track with preview and link"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Display album art
        if track["album"]["images"]:
            st.image(track["album"]["images"][0]["url"], width=150)
    
    with col2:
        # Track info
        st.markdown(f"### {index}. {track['name']}")
        st.markdown(f"**Artist(s):** {', '.join([artist['name'] for artist in track['artists']])}")
        st.markdown(f"**Album:** {track['album']['name']}")
        
        # Links and preview
        col_link, col_preview = st.columns(2)
        
        with col_link:
            st.markdown(f"🔗 [Open in Spotify]({track['external_urls']['spotify']})")
        
        with col_preview:
            if track.get("preview_url"):
                st.audio(track["preview_url"], format="audio/mp3")
            else:
                st.caption("🔇 No preview available")
        
        st.divider()


def main():
    """Main application"""
    # Handle OAuth callback redirect
    query_params = st.query_params
    if 'code' in query_params:
        # User was redirected back from Spotify OAuth
        st.success("✅ Spotify successfully connected! Processing authorization...")
        # The auth code will be processed below in the normal flow
    
    # Handle OAuth errors
    if 'error' in query_params:
        error_type = query_params.get('error', 'unknown')
        st.error(f"❌ Spotify authorization failed: {error_type}")
        if error_type == "access_denied":
            st.info("You declined the authorization request. Click 'Connect Spotify' to try again.")
        st.query_params.clear()
    
    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'liked_track_ids' not in st.session_state:
        st.session_state.liked_track_ids = []
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0  # Default to first tab
    
    # Header
    st.title("🎵 Spotify Mood-Based Track Recommender")
    st.markdown("Discover new music tailored to your current mood!")
    
    # Try to initialize OAuth client
    try:
        sp, auth_manager = get_spotify_client()
        
        # Show current configuration in debug mode (only in sidebar)
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', '(missing)')
        
        # Check if user needs to authenticate
        token_info = auth_manager.get_cached_token()
        
        if not token_info:
            # Show login button and helpful info
            st.info("🔐 Connect your Spotify account to use your Liked Songs for personalized recommendations!")
            
            # Show troubleshooting in expander
            with st.expander("⚙️ Troubleshooting OAuth Connection"):
                st.markdown(f"""
                **Current Redirect URI:** `{redirect_uri}`
                
                **If you see "INVALID_CLIENT" error:**
                
                1. **Check Spotify Developer Dashboard:**
                   - Go to: https://developer.spotify.com/dashboard
                   - Open your app settings
                   - Under "Redirect URIs", make sure this EXACT URL is added:
                     ```
                     {redirect_uri}
                     ```
                   - Click "Save" after adding
                
                2. **Check your Streamlit Secrets:**
                   - SPOTIPY_CLIENT_ID must match your Spotify app's Client ID
                   - SPOTIPY_CLIENT_SECRET must match your Spotify app's Client Secret
                   - SPOTIPY_REDIRECT_URI must be: `https://your-app-name.streamlit.app`
                
                3. **Common Issues:**
                   - ❌ Redirect URI has trailing slash (don't include `/`)
                   - ❌ Using `http://` instead of `https://` for Streamlit Cloud
                   - ❌ Copy-paste error in Client ID or Secret (check for spaces)
                   - ❌ Forgot to click "Save" in Spotify Dashboard
                
                **Note:** App works fine without OAuth! You'll get search-based recommendations.
                """)
            
            if st.button("🔐 Connect Spotify", type="primary"):
                auth_url = auth_manager.get_authorize_url()
                st.markdown(f"""
                ### Click the link below to authorize:
                [🎵 Authorize with Spotify]({auth_url})
                
                You'll be redirected back after authorization.
                """)
            
            # Check for auth code in query params
            if 'code' in query_params:
                code = query_params['code']
                try:
                    with st.spinner("Completing authorization..."):
                        token_info = auth_manager.get_access_token(code, as_dict=True)
                        st.session_state.logged_in = True
                        # Clear the code from URL and refresh
                        st.query_params.clear()
                        st.success("✅ Successfully connected to Spotify!")
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to authenticate: {e}")
                    st.error("""
                    **Common causes:**
                    - Client ID or Secret mismatch
                    - Redirect URI not added to Spotify Dashboard
                    - Expired authorization code (try again)
                    """)
            
            # Use client credentials fallback for non-logged-in users
            sp = get_spotify_client_credentials_only()
            use_liked_songs = False
        else:
            st.session_state.logged_in = True
            use_liked_songs = True
            
            # Fetch user profile if not already fetched
            if not st.session_state.user_profile:
                with st.spinner("Loading your profile..."):
                    st.session_state.user_profile = get_user_profile(sp)
            
            # Fetch liked songs if not already fetched
            if not st.session_state.liked_track_ids:
                with st.spinner("Fetching your Liked Songs..."):
                    st.session_state.liked_track_ids = get_user_liked_track_ids(sp, max_ids=300)
                if st.session_state.liked_track_ids:
                    st.success(f"✅ Loaded {len(st.session_state.liked_track_ids)} Liked Songs!")
    except Exception as e:
        st.warning(f"OAuth not available: {e}. Using basic mode.")
        sp = get_spotify_client_credentials_only()
        use_liked_songs = False
    
    # Sidebar for mood selection and feature customization
    with st.sidebar:
        # Show login status and profile
        if st.session_state.logged_in and st.session_state.user_profile:
            profile = st.session_state.user_profile
            
            # Display profile picture
            if profile.get("profile_image"):
                st.image(profile["profile_image"], width=80)
            else:
                # Show default emoji placeholder if no profile image
                st.markdown("# 👤")
            
            # Display greeting with user's display name
            display_name = profile.get("display_name", "Spotify User")
            st.markdown(f"👋 Logged in as **{display_name}**")
            
            # Additional profile info
            st.caption(f"{len(st.session_state.liked_track_ids)} Liked Songs")
            
            # Profile link and refresh button
            if profile.get("url"):
                st.markdown(f"[View on Spotify]({profile['url']})")
            
            if st.button("🔄 Refresh", key="refresh_profile"):
                st.session_state.liked_track_ids = get_user_liked_track_ids(sp, max_ids=300)
                st.session_state.user_profile = get_user_profile(sp)
                st.rerun()
            
            st.success("✅ Connected")
        else:
            st.info("ℹ️ Not logged in - using search mode")
        
        st.divider()
        st.header("🎭 Select Your Mood")
        
        # Mood selection
        selected_mood = st.selectbox(
            "Choose a mood:",
            options=list(MOOD_PRESETS.keys()),
            help="Select the mood that matches how you're feeling"
        )
        
        st.caption(MOOD_PRESETS[selected_mood]["description"])
        st.divider()
        
        # Feature customization
        st.header("🎚️ Customize Features")
        st.caption("Fine-tune the audio characteristics")
        
        # Get preset values
        preset = MOOD_PRESETS[selected_mood]
        
        # Sliders for each feature
        valence = st.slider(
            "Valence (Positivity)",
            min_value=0.0,
            max_value=1.0,
            value=preset["valence"],
            step=0.1,
            help="Musical positiveness (0 = sad, 1 = happy)"
        )
        
        energy = st.slider(
            "Energy",
            min_value=0.0,
            max_value=1.0,
            value=preset["energy"],
            step=0.1,
            help="Intensity and activity level"
        )
        
        danceability = st.slider(
            "Danceability",
            min_value=0.0,
            max_value=1.0,
            value=preset["danceability"],
            step=0.1,
            help="How suitable the track is for dancing"
        )
        
        tempo = st.slider(
            "Tempo (BPM)",
            min_value=60,
            max_value=200,
            value=preset["tempo"],
            step=5,
            help="Speed of the track in beats per minute"
        )
        
        st.divider()
        
        # Number of recommendations
        num_tracks = st.slider(
            "Number of tracks",
            min_value=5,
            max_value=20,
            value=10,
            help="How many recommendations to show"
        )
        
        # Get recommendations button
        get_recs = st.button("🎲 Get Recommendations", type="primary", use_container_width=True)
    
    # Main content area - Use session state for tab selection
    st.divider()
    
    # Mode selector with clear visual separation
    mode = st.radio(
        "Choose Your Experience:",
        ["🎭 Manual Mode", "💬 Chatbot Mode"],
        horizontal=True,
        key="mode_selector",
        help="Manual: Use sliders to customize. Chatbot: Just type what you want!"
    )
    
    st.divider()
    
    # Show the selected mode
    if mode == "🎭 Manual Mode":
        # Original manual mood selection flow
        _display_manual_mode(get_recs, selected_mood, valence, energy, danceability, tempo, num_tracks, sp, st.session_state.logged_in, st.session_state.liked_track_ids)
    else:
        # New chatbot interface
        _display_chatbot_mode(sp, st.session_state.logged_in, st.session_state.liked_track_ids)


def _display_manual_mode(get_recs, selected_mood, valence, energy, danceability, tempo, num_tracks, sp, is_logged_in, liked_track_ids):
    """Display the original manual mood selection interface"""
    if get_recs:
        # Prepare feature dictionary
        mood_features = {
            "valence": valence,
            "energy": energy,
            "danceability": danceability,
            "tempo": tempo
        }
        
        # Show loading spinner
        with st.spinner("🔍 Finding perfect tracks for you..."):
            tracks = get_recommendations(
                sp, 
                mood_features, 
                selected_mood=selected_mood, 
                limit=num_tracks,
                use_liked_songs=is_logged_in,
                liked_track_ids=liked_track_ids
            )
        
        if tracks:
            st.success(f"✨ Found {len(tracks)} tracks for your {selected_mood} mood!")
            
            # Add save to playlist button (only if logged in)
            if is_logged_in and st.session_state.user_profile:
                if st.button("💾 Save these tracks as a private playlist"):
                    try:
                        me = sp.current_user()
                        user_id = me["id"]
                        name = f"Mood2Music – {selected_mood}"
                        pl = sp.user_playlist_create(user=user_id, name=name, public=False, description="Created by Mood2Music")
                        sp.playlist_add_items(pl["id"], [t["id"] for t in tracks if t.get("id")])
                        st.success(f"Saved! Open in Spotify: {pl['external_urls']['spotify']}")
                    except Exception as e:
                        st.error(f"Failed to create playlist: {e}")
            
            # Display feature summary
            with st.expander("📊 Current Audio Features"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Valence", f"{valence:.1f}")
                col2.metric("Energy", f"{energy:.1f}")
                col3.metric("Danceability", f"{danceability:.1f}")
                col4.metric("Tempo", f"{tempo} BPM")
            
            st.divider()
            
            # Display tracks
            for idx, track in enumerate(tracks, 1):
                display_track(track, idx)
        else:
            st.warning("No tracks found. Try adjusting the features!")
    else:
        # Welcome message
        st.info("👈 Select a mood and click 'Get Recommendations' to start discovering music!")
        
        # Display mood presets info
        st.header("Available Moods")
        cols = st.columns(3)
        for idx, (mood, preset) in enumerate(MOOD_PRESETS.items()):
            with cols[idx % 3]:
                st.markdown(f"**{mood}**")
                st.caption(preset["description"])


def _display_chatbot_mode(sp, is_logged_in, liked_track_ids):
    """Display the AI chatbot interface for natural language music requests"""
    
    # Styled header with emoji
    st.markdown("### 💬 AI Music Assistant")
    st.caption("Ask me for any mood, activity, or artist - I'll find the perfect tracks!")
    
    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        # Add welcome message
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": "👋 Hi! I'm your music assistant. I can help you find music in two ways:\n\n**1️⃣ By Mood/Activity:**\n- 'I need workout music'\n- 'Something chill to study to'\n- 'Happy songs for a party'\n\n**2️⃣ By Artist:**\n- 'Play Rauw Alejandro songs'\n- 'Music by Bad Bunny'\n- 'Listen to Taylor Swift'\n\nWhat are you in the mood for? 🎵"
        })
    
    # Connection status with better styling
    if not is_logged_in:
        with st.expander("💡 Pro Tip: Get Personalized Results", expanded=False):
            st.info("Connect your Spotify account to get recommendations from YOUR liked songs library!")
            st.caption("Without connecting, I can still search all of Spotify for any artist or mood.")
    else:
        st.success(f"✅ Connected • {len(liked_track_ids)} songs in your library")
    
    st.divider()
    
    # Clear chat button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Clear", help="Clear chat history", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    # Chat container with scrollable area
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display tracks if they exist in the message
                if "tracks" in message:
                    for idx, track in enumerate(message["tracks"], 1):
                        display_track(track, idx)
    
    # Chat input
    if prompt := st.chat_input("What kind of music are you looking for?"):
        # Add user message to chat
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the request
        with st.chat_message("assistant"):
            with st.spinner("🎵 Finding songs for you..."):
                # Check if user is asking for a specific artist
                artist_name = extract_artist_from_text(prompt)
                
                if artist_name:
                    # Artist-specific search
                    try:
                        results = sp.search(q=f"artist:{artist_name}", limit=10, type='track', market='US')
                        tracks = results.get('tracks', {}).get('items', [])
                        
                        if tracks:
                            response = f"🎵 Found {len(tracks)} songs by {artist_name}!"
                            st.markdown(response)
                            
                            # Display tracks
                            for idx, track in enumerate(tracks, 1):
                                display_track(track, idx)
                            
                            # Save assistant message with tracks
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": response,
                                "tracks": tracks
                            })
                        else:
                            response = f"😔 Couldn't find any songs by '{artist_name}'. Try checking the spelling or try a different artist!"
                            st.markdown(response)
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": response
                            })
                    except Exception as e:
                        response = f"❌ Error searching for artist: {e}"
                        st.markdown(response)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": response
                        })
                else:
                    # Mood-based recommendation
                    mood_name, mood_features, explanation = parse_mood_from_text(prompt)
                    
                    # Try getting recommendations from liked songs first
                    tracks = []
                    if liked_track_ids and len(liked_track_ids) >= 5:
                        tracks = filter_liked_songs_by_mood(sp, liked_track_ids, mood_features, limit=10)
                    
                    # If no tracks from liked songs, fall back to search
                    if not tracks:
                        st.info("🔍 Searching Spotify for mood-matching tracks...")
                        try:
                            tracks = get_recommendations(
                                sp,
                                mood_features,
                                selected_mood=mood_name,
                                limit=10,
                                use_liked_songs=False,  # Force search mode
                                liked_track_ids=[]
                            )
                        except Exception as e:
                            st.error(f"Search failed: {e}")
                    
                    if tracks:
                        # Generate friendly response
                        if liked_track_ids and len(liked_track_ids) >= 5:
                            response = generate_chatbot_response(prompt, tracks, mood_name)
                        else:
                            response = f"🎵 Found {len(tracks)} {mood_name.lower()} tracks from Spotify!"
                        
                        st.markdown(f"{explanation}\n\n{response}")
                        
                        # Display tracks
                        for idx, track in enumerate(tracks, 1):
                            display_track(track, idx)
                        
                        # Save assistant message with tracks
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": f"{explanation}\n\n{response}",
                            "tracks": tracks
                        })
                    else:
                        response = f"😔 Sorry, I couldn't find any {mood_name.lower()} tracks. Try a different mood or be more specific!"
                        st.markdown(response)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": response
                        })
    
    # Add clear chat button
    if len(st.session_state.chat_messages) > 1:  # More than just welcome message
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = [{
                "role": "assistant",
                "content": "👋 Chat cleared! What music are you looking for?"
            }]
            st.rerun()


if __name__ == "__main__":
    main()
