import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

print(f"Client ID: {client_id[:10]}..." if client_id else "No Client ID")
print(f"Client Secret: {client_secret[:10]}..." if client_secret else "No Client Secret")

try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))
    
    # Test basic search
    print("\n✅ Testing Spotify API connection...")
    results = sp.search(q='test', limit=1, type='track')
    if results and results.get('tracks'):
        print("✅ Search API works!")
        
    # Test recommendations with seed_tracks instead of genres
    print("\n✅ Testing recommendations API with seed_tracks...")
    recs = sp.recommendations(seed_tracks=['11dFghVXANMlKmJXsNCbNl'], limit=5, market='US')
    if recs and recs.get('tracks'):
        print(f"✅ Recommendations with tracks works! Got {len(recs['tracks'])} tracks")
    
    # Test genre seeds endpoint
    print("\n✅ Testing genre seeds...")
    genres = sp.recommendation_genre_seeds()
    if genres:
        print(f"✅ Genre seeds works! Found {len(genres['genres'])} genres")
        print(f"First 10 genres: {genres['genres'][:10]}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
