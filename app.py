"""
Spotify Mood-Based Track Recommender
A Streamlit app that recommends tracks based on selected mood and customizable audio features.
"""

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import os
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
        
        # Use OAuth for user authentication (allows access to liked songs, top tracks, and playlist creation)
        auth_manager = SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=redirect_uri,
            scope="user-library-read user-top-read playlist-modify-private",
            cache_path=".cache_streamlit",
            show_dialog=True
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


def get_recommendations(sp, mood_features, selected_mood="Happy", limit=10, use_liked_songs=False, liked_track_ids=None):
    """Get track recommendations using liked songs with improved seed selection"""
    try:
        # If user is logged in and has liked songs, use them as seeds
        if use_liked_songs and liked_track_ids:
            all_liked_count = len(liked_track_ids)
            
            # Get audio features safely
            audio_features_list = safe_audio_features(sp, liked_track_ids)
            features_count = len(audio_features_list)
            
            # Determine seed source
            seed_source = "genres"
            seed_tracks = []
            
            # Try liked-song features first → pick up to 5 seed_tracks
            if features_count >= 3:
                # Pick up to 5 random tracks from those with features
                import random
                available_ids = [f["id"] for f in audio_features_list if f and f.get("id")]
                seed_tracks = random.sample(available_ids, min(5, len(available_ids)))
                seed_source = "Liked Songs"
            
            # If len(features) < 3, use top tracks fallback
            if len(audio_features_list) < 3:
                top = get_top_track_ids(sp, 50)
                if top:
                    seed_tracks = top[:5]
                    seed_source = "top-tracks"
            
            # Show metrics to user BEFORE showing results
            st.caption(f"Liked: {all_liked_count} • Valid IDs: {all_liked_count} • Feature rows: {features_count} • Seed: {seed_source}")
            
            # If we have seeds, try recommendations API with market="US"
            if len(seed_tracks) >= 1:
                try:
                    # Build recommendation parameters
                    rec_params = {
                        "seed_tracks": seed_tracks,
                        "limit": limit,
                        "market": "US"
                    }
                    
                    # Add target features (only if significantly different from neutral)
                    if abs(mood_features["valence"] - 0.5) > 0.1:
                        rec_params["target_valence"] = mood_features["valence"]
                    if abs(mood_features["energy"] - 0.5) > 0.1:
                        rec_params["target_energy"] = mood_features["energy"]
                    if abs(mood_features["danceability"] - 0.5) > 0.1:
                        rec_params["target_danceability"] = mood_features["danceability"]
                    if abs(mood_features["tempo"] - 120) > 20:
                        rec_params["target_tempo"] = mood_features["tempo"]
                    
                    results = sp.recommendations(**rec_params)
                    tracks = results.get("tracks", [])
                    
                    if tracks:
                        return tracks[:limit]
                    
                except Exception as e:
                    st.warning(f"Recommendations API failed: {e}. Falling back to search...")
        
        # Fallback to search-based approach
        # Get official Spotify genre list
        available_genres = get_available_genres(sp)
        
        # Use seed genres based on mood characteristics  
        user_genres = ["pop", "indie-pop", "electronic"]
        seed_genres = normalize_genres(user_genres, available_genres)
        
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
                limit=min(limit * 3, 50),  # Get more results to filter
                type='track',
                market='US'
            )
            tracks = results.get('tracks', {}).get('items', [])
        except Exception as e:
            st.warning(f"Initial search failed: {e}")
        
        # Attempt 2: If no tracks, try without year filter (broader search)
        if not tracks:
            st.info("🔄 Expanding search criteria...")
            try:
                results = sp.search(
                    q=search_query,
                    limit=min(limit * 3, 50),
                    type='track',
                    market='US'
                )
                tracks = results.get('tracks', {}).get('items', [])
            except Exception as e:
                st.warning(f"Broader search failed: {e}")
        
        # Attempt 3: If still no tracks, use generic mood keyword only
        if not tracks:
            st.info("🔄 Using broader mood search...")
            try:
                generic_query = selected_mood.lower()
                results = sp.search(
                    q=generic_query,
                    limit=min(limit * 3, 50),
                    type='track',
                    market='US'
                )
                tracks = results.get('tracks', {}).get('items', [])
            except Exception as e:
                st.warning(f"Generic search failed: {e}")
        
        # Attempt 4: Last resort - search for "top hits" with no filters
        if not tracks:
            st.info("🔄 Finding popular tracks as fallback...")
            try:
                results = sp.search(
                    q="top hits 2024",
                    limit=min(limit * 2, 50),
                    type='track',
                    market='US'
                )
                tracks = results.get('tracks', {}).get('items', [])
                if tracks:
                    st.warning("⚠️ No exact matches found. Showing popular tracks instead.")
            except Exception as e:
                st.error(f"All search attempts failed: {e}")
        
        if not tracks:
            st.error("❌ Unable to find any tracks. Please try again later or adjust your settings.")
            return []
        
        # Filter tracks by availability
        filtered_tracks = []
        for track in tracks:
            if track and track.get('id') and track.get('name'):
                filtered_tracks.append(track)
                if len(filtered_tracks) >= limit:
                    break
        
        # If we got results but from fallback, show success message
        if filtered_tracks and len(filtered_tracks) >= limit:
            return filtered_tracks[:limit]
        elif filtered_tracks:
            st.info(f"ℹ️ Found {len(filtered_tracks)} tracks (requested {limit}). Showing all available results.")
            return filtered_tracks
        else:
            st.warning("⚠️ No valid tracks found in search results.")
            return []
        
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
    
    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'liked_track_ids' not in st.session_state:
        st.session_state.liked_track_ids = []
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    
    # Header
    st.title("🎵 Spotify Mood-Based Track Recommender")
    st.markdown("Discover new music tailored to your current mood!")
    
    # Debug: Show redirect URI being used
    st.caption(f"Redirect URI: {os.getenv('SPOTIPY_REDIRECT_URI', '(missing)')}")
    
    # Try to initialize OAuth client
    try:
        sp, auth_manager = get_spotify_client()
        
        # Check if user needs to authenticate
        token_info = auth_manager.get_cached_token()
        
        if not token_info:
            # Show login button
            st.info("🔐 Connect your Spotify account to use your Liked Songs as seeds for better recommendations!")
            
            if st.button("🔐 Connect Spotify", type="primary"):
                print("Authorize URL redirect_uri =", os.getenv("SPOTIPY_REDIRECT_URI"))
                auth_url = auth_manager.get_authorize_url()
                st.markdown(f"[Click here to authorize with Spotify]({auth_url})")
                st.info("After authorizing, you'll be redirected back automatically.")
            
            # Check for auth code in query params
            if 'code' in query_params:
                code = query_params['code']
                try:
                    token_info = auth_manager.get_access_token(code, as_dict=True)
                    st.session_state.logged_in = True
                    # Clear the code from URL and refresh
                    st.query_params.clear()
                    st.success("✅ Successfully connected to Spotify!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to authenticate: {e}")
            
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
    
    # Main content area
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
                use_liked_songs=st.session_state.logged_in,
                liked_track_ids=st.session_state.liked_track_ids
            )
        
        if tracks:
            st.success(f"✨ Found {len(tracks)} tracks for your {selected_mood} mood!")
            
            # Add save to playlist button (only if logged in)
            if st.session_state.logged_in and st.session_state.user_profile:
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


if __name__ == "__main__":
    main()
