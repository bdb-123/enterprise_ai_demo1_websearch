# 🤖 AI Chatbot Feature

## Overview
The Spotify Mood2Music app now includes an **AI Chatbot** that understands natural language requests and recommends songs from YOUR liked songs library!

## Features

### 💬 Natural Language Understanding
Talk to the bot like you would to a friend:
- **"I need workout music"** → Gets high-energy tracks
- **"Something chill to study to"** → Finds calm, focus-enhancing songs
- **"Happy songs for a party"** → Picks upbeat, danceable tracks
- **"Sad songs to cry to"** → Selects melancholic, emotional music
- **"Romantic tracks for a date night"** → Chooses love songs

### 🎯 Smart Mood Detection
The chatbot recognizes:

**Activity Keywords:**
- workout, gym, exercise, running → **Hype** mood
- study, work, coding, reading → **Focus** mood
- sleep, meditate, yoga → **Chill** mood
- party, dance, celebrate → **Happy** mood
- date, dinner, romance → **Romantic** mood

**Mood Keywords:**
- happy, joyful, cheerful, excited
- chill, relax, calm, peaceful
- focus, concentrate, productivity
- sad, melancholy, emotional, heartbreak
- hype, energetic, pump, intense
- romantic, love, intimate

### 🎵 Personalized Recommendations
- Only recommends songs from **YOUR** liked songs library
- Uses audio features (valence, energy, danceability, tempo) to match mood
- Shows up to 10 best-matching tracks per request

### 💾 Chat History
- Remembers your conversation
- Can clear history with "Clear Chat History" button
- Displays previous recommendations in chat

## How to Use

### Step 1: Connect Your Spotify Account
1. Click "🔐 Connect Spotify" in the sidebar
2. Authorize the app
3. Your liked songs will be loaded

### Step 2: Open the Chatbot Tab
1. Click the "💬 AI Chatbot" tab at the top
2. You'll see a welcome message

### Step 3: Chat Away!
Type any of these examples:

```
"I'm going to the gym, need some pump-up music"
"Show me relaxing songs for studying"
"What happy songs do I have?"
"I want something romantic"
"Give me sad songs"
"Energetic tracks for running"
```

### Step 4: Enjoy Your Music!
- Click album art to preview
- Click "Open in Spotify" to play in Spotify app
- Use audio preview player if available

## Example Conversations

### Conversation 1: Workout Music
**You:** "I'm about to workout, give me some hype music"

**Bot:** "Perfect for workout! Setting mood to Hype.

🔥 Found 10 high-energy bangers!

[Shows your liked songs with high energy, high tempo]"

### Conversation 2: Study Session
**You:** "I need focus music for studying"

**Bot:** "Detected Focus mood from your request!

🎯 Found 10 tracks to boost your concentration

[Shows your liked songs with moderate energy, low valence]"

### Conversation 3: Romantic Evening
**You:** "date night music please"

**Bot:** "Perfect for date! Setting mood to Romantic.

❤️ Found 10 romantic tracks for you

[Shows your liked songs with moderate valence, lower energy]"

## Technical Details

### How Mood Extraction Works
1. **Text Analysis**: Scans your message for activity and mood keywords
2. **Mood Mapping**: Maps keywords to preset moods (Happy, Chill, Focus, Sad, Hype, Romantic)
3. **Feature Selection**: Selects appropriate audio features:
   - **Happy**: valence=0.8, energy=0.7, danceability=0.7, tempo=120
   - **Chill**: valence=0.5, energy=0.3, danceability=0.4, tempo=90
   - **Focus**: valence=0.4, energy=0.4, danceability=0.3, tempo=100
   - **Sad**: valence=0.2, energy=0.3, danceability=0.3, tempo=80
   - **Hype**: valence=0.7, energy=0.9, danceability=0.8, tempo=140
   - **Romantic**: valence=0.6, energy=0.4, danceability=0.5, tempo=95

### How Recommendations Work
1. **Library Sampling**: Gets up to 100 random songs from your liked songs
2. **Audio Analysis**: Fetches audio features from Spotify API
3. **Scoring**: Calculates match score for each song:
   ```python
   score = abs(track_valence - target_valence) * 2.0 +
           abs(track_energy - target_energy) * 1.5 +
           abs(track_danceability - target_danceability) * 1.2
   ```
4. **Ranking**: Sorts by best match (lowest score = best match)
5. **Selection**: Returns top 10 matches

### Session State
- Chat history stored in `st.session_state.chat_messages`
- Persists during session
- Can be cleared by user

## Requirements

### Must Be Logged In
The chatbot **requires** Spotify OAuth connection because:
- Needs access to your liked songs library
- Fetches audio features for your tracks
- Personalizes recommendations to YOUR music taste

### Minimum Library Size
- Need at least 5 liked songs for chatbot to work
- More songs = better recommendations
- Recommends having 50+ liked songs for best experience

## Limitations

### What the Chatbot CAN'T Do (Yet)
- ❌ Can't search Spotify catalog (only YOUR liked songs)
- ❌ Can't create playlists directly from chat (use manual mode for that)
- ❌ Can't remember preferences across sessions
- ❌ Can't understand complex multi-criteria requests
- ❌ Can't handle follow-up modifications ("make it more upbeat")

### Current Capabilities
- ✅ Understands mood keywords and activities
- ✅ Filters YOUR liked songs by mood
- ✅ Displays chat history during session
- ✅ Shows audio previews and Spotify links
- ✅ Fast and responsive

## Comparison: Manual vs Chatbot Mode

| Feature | Manual Mode | Chatbot Mode |
|---------|-------------|--------------|
| **Interface** | Sliders & dropdowns | Natural language chat |
| **Song Source** | Search OR liked songs | Only YOUR liked songs |
| **Mood Selection** | 6 preset moods | Free-form text input |
| **Customization** | Full control over features | Automatic mood mapping |
| **Save Playlist** | ✅ Yes | ❌ Not yet |
| **Best For** | Fine-tuning, discovering new music | Quick requests, personal library |

## Tips for Best Results

### 🎯 Be Specific
- ✅ "I need energetic workout music"
- ❌ "music"

### 🎵 Add More Liked Songs
The more liked songs you have, the better the recommendations!

### 🔄 Try Different Phrasings
If results aren't great, try rephrasing:
- "workout music" → "gym tracks" → "high energy songs"
- "sad songs" → "emotional music" → "melancholy tracks"

### 💡 Use Activity Keywords
Activity keywords work great:
- "running", "studying", "dating", "sleeping", "partying"

## Future Enhancements

Planned features:
- [ ] OpenAI GPT integration for smarter mood detection
- [ ] Multi-turn conversation with context
- [ ] "More like this" follow-up requests
- [ ] Custom audio feature adjustments via chat
- [ ] Playlist creation from chat
- [ ] Search Spotify catalog option
- [ ] Voice input support
- [ ] Mood intensity control ("very happy" vs "slightly happy")

## Troubleshooting

### "Please connect your Spotify account"
**Solution:** Click "Connect Spotify" in sidebar and authorize the app

### "You don't have enough liked songs yet"
**Solution:** Add more songs to your Spotify library (need minimum 5 songs)

### "Couldn't find any songs matching X mood"
**Possible causes:**
- You don't have songs that match that mood in your library
- Your liked songs all have similar audio features
- Try a different mood or add more variety to your library

### Chatbot not responding
**Solution:** 
- Check if you're logged in
- Reload the page
- Clear chat history and try again

## FAQ

**Q: Can I use the chatbot without connecting Spotify?**
A: No, the chatbot needs access to your liked songs library.

**Q: Does the chatbot use AI/GPT?**
A: Currently uses keyword matching. GPT integration planned for future!

**Q: Can it create playlists?**
A: Not yet, but you can use Manual Mode to save playlists.

**Q: How accurate is mood detection?**
A: Very good for simple requests. Complex requests may need rephrasing.

**Q: Does it learn my preferences?**
A: Not yet - uses Spotify's audio features for matching.

**Q: Can I request specific genres?**
A: Yes! Try "give me some rock songs" or "show me jazz tracks"

## Enjoy!

Have fun discovering music in your library with the AI chatbot! 🎵🤖
