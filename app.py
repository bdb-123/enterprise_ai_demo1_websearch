"""
Spotify Mood-Based Track Recommender
A Streamlit app that recommends tracks based on selected mood and customizable audio features.
"""

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
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
    """Initialize and cache Spotify client"""
    try:
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            st.error("⚠️ Spotify credentials not found!")
            st.info("Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables.")
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


def get_recommendations(sp, mood_features, limit=10):
    """Get track recommendations based on mood features"""
    try:
        # Use seed genres based on mood characteristics
        seed_genres = ["pop", "indie", "electronic"]
        
        results = sp.recommendations(
            seed_genres=seed_genres,
            limit=limit,
            target_valence=mood_features["valence"],
            target_energy=mood_features["energy"],
            target_danceability=mood_features["danceability"],
            target_tempo=mood_features["tempo"]
        )
        
        return results["tracks"]
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return []


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
    # Header
    st.title("🎵 Spotify Mood-Based Track Recommender")
    st.markdown("Discover new music tailored to your current mood!")
    
    # Initialize Spotify client
    sp = get_spotify_client()
    
    # Sidebar for mood selection and feature customization
    with st.sidebar:
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
            tracks = get_recommendations(sp, mood_features, limit=num_tracks)
        
        if tracks:
            st.success(f"✨ Found {len(tracks)} tracks for your {selected_mood} mood!")
            
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
