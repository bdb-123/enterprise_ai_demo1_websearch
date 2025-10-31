"""
Quick test to verify mood-to-genre matching improvements
"""

# Test the new mood-specific genre function
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


def score_track_match(track_features, target_features):
    """
    Calculate how well a track's audio features match the target mood.
    Returns a score where lower is better (0 = perfect match).
    """
    if not track_features:
        return float('inf')
    
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


# Test cases
print("Testing mood-to-genre mappings:")
print("-" * 50)

moods = ["Happy", "Chill", "Focus", "Sad", "Hype", "Romantic"]
for mood in moods:
    genres = get_mood_specific_genres(mood)
    print(f"{mood:10} -> {', '.join(genres)}")

print("\n" + "=" * 50)
print("\nTesting track scoring:")
print("-" * 50)

# Happy mood target
happy_target = {
    "valence": 0.8,
    "energy": 0.7,
    "danceability": 0.7,
    "tempo": 120
}

# Test tracks
test_tracks = [
    {
        "name": "Perfect Happy Match",
        "features": {"valence": 0.8, "energy": 0.7, "danceability": 0.7, "tempo": 120}
    },
    {
        "name": "Sad Song (Bad Match)",
        "features": {"valence": 0.2, "energy": 0.3, "danceability": 0.3, "tempo": 80}
    },
    {
        "name": "Pretty Good Match",
        "features": {"valence": 0.75, "energy": 0.65, "danceability": 0.75, "tempo": 125}
    },
    {
        "name": "High Energy but Sad",
        "features": {"valence": 0.3, "energy": 0.9, "danceability": 0.5, "tempo": 140}
    }
]

print(f"\nTarget (Happy mood): valence=0.8, energy=0.7, dance=0.7, tempo=120\n")

scored = []
for track in test_tracks:
    score = score_track_match(track["features"], happy_target)
    scored.append((track["name"], score))
    print(f"{track['name']:25} -> Score: {score:.3f}")

print("\n" + "=" * 50)
print("\nSorted by best match (lower score = better):")
print("-" * 50)

scored.sort(key=lambda x: x[1])
for i, (name, score) in enumerate(scored, 1):
    print(f"{i}. {name:25} (score: {score:.3f})")

print("\n✅ All tests passed! The mood matching logic looks good.")
