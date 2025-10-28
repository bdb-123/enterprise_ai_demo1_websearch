# 🎵 Spotify Mood-Based Track Recommender

A Streamlit web application that recommends Spotify tracks based on your current mood. Select from six different moods and fine-tune audio features to discover new music perfectly matched to how you're feeling!

## ✨ Features

- **6 Mood Presets**: Happy, Chill, Focus, Sad, Hype, and Romantic
- **Audio Feature Customization**: Adjust valence, energy, danceability, and tempo with interactive sliders
- **30-Second Previews**: Listen to track samples directly in the app (when available)
- **Direct Spotify Links**: Quick access to full tracks on Spotify
- **Album Artwork**: Visual display of each recommended track
- **Responsive Design**: Clean, modern interface that works on all devices

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A Spotify Developer account (free)

### 1. Get Spotify API Credentials

To use this app, you need Spotify API credentials:

1. **Create a Spotify Account** (if you don't have one):
   - Go to [spotify.com](https://www.spotify.com) and sign up

2. **Access the Spotify Developer Dashboard**:
   - Visit [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
   - Log in with your Spotify account

3. **Create a New App**:
   - Click "Create app"
   - Fill in the details:
     - **App name**: "Mood Track Recommender" (or your choice)
     - **App description**: "A mood-based music recommendation app"
     - **Redirect URI**: `http://localhost:8501` (for local development)
   - Check the box to agree to Spotify's Terms of Service
   - Click "Save"

4. **Get Your Credentials**:
   - On your app's dashboard, click "Settings"
   - You'll see your **Client ID** (visible)
   - Click "View client secret" to reveal your **Client Secret**
   - **Important**: Keep your Client Secret private! Never commit it to version control

---

### 2. Run the App Locally

#### Step 1: Clone or Download the Project

```bash
# If using git
git clone <your-repo-url>
cd <project-directory>

# Or simply navigate to the project folder if you already have it
```

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Set Environment Variables

**Option A: Using Terminal (Temporary - lasts for current session)**

**macOS/Linux:**
```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
```

**Windows (Command Prompt):**
```cmd
set SPOTIFY_CLIENT_ID=your_client_id_here
set SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

**Windows (PowerShell):**
```powershell
$env:SPOTIFY_CLIENT_ID="your_client_id_here"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret_here"
```

**Option B: Using a .env file (Recommended for development)**

1. Install python-dotenv:
   ```bash
   pip install python-dotenv
   ```

2. Create a `.env` file in the project root:
   ```
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```

3. Add `.env` to your `.gitignore` file to prevent committing secrets

#### Step 4: Run the Streamlit App

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Community Cloud

Deploy your app for free and share it with the world!

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (make sure `.env` is in `.gitignore`!)
2. Ensure these files are in your repo:
   - `app.py`
   - `requirements.txt`
   - `README.md`

### Step 2: Deploy on Streamlit Cloud

1. **Sign up for Streamlit Community Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

2. **Create a New App**:
   - Click "New app"
   - Select your repository
   - Choose the branch (usually `main`)
   - Set the main file path: `app.py`

3. **Add Secrets (API Credentials)**:
   - Click "Advanced settings"
   - In the "Secrets" section, add:
     ```toml
     SPOTIFY_CLIENT_ID = "your_client_id_here"
     SPOTIFY_CLIENT_SECRET = "your_client_secret_here"
     ```
   - Click "Deploy"

4. **Wait for Deployment**:
   - Streamlit will build and deploy your app (usually takes 1-2 minutes)
   - You'll get a public URL like `your-app-name.streamlit.app`

### Step 3: Share Your App!

Your app is now live and accessible to anyone with the URL!

---

## 🎬 Demo Script for Presentation Day (3-5 Minutes)

Use this script to deliver a compelling demo of your Spotify Mood Recommender:

### **Minute 1: Introduction (30 seconds)**

> "Hi everyone! Today I'm excited to show you my Spotify Mood-Based Track Recommender. Have you ever struggled to find the right music for your mood? This app solves that problem by using Spotify's powerful recommendation API combined with audio feature analysis to deliver perfectly matched tracks."

**[Show the app homepage]**

### **Minute 2: The Problem & Solution (45 seconds)**

> "The problem: Spotify has 100 million tracks, but finding the right one for your current mood can be overwhelming. My solution leverages Spotify's audio features—things like valence (musical positivity), energy, danceability, and tempo—to mathematically match music to your emotional state."

**[Point to the mood selector in the sidebar]**

### **Minute 3: Live Demo - Preset Mood (60 seconds)**

> "Let me show you how it works. Let's say I'm feeling 'Happy' today."

**[Select "Happy" mood]**

> "Notice the preset values: high valence (0.8) for positivity, solid energy (0.7), and an upbeat tempo of 120 BPM. Now I'll click 'Get Recommendations'..."

**[Click button and wait for results]**

> "And there we have it! Ten tracks perfectly matched to a happy mood. You can see the album artwork, artist info, and most importantly—here's a 30-second preview."

**[Play one audio preview]**

> "If you love a track, click this Spotify link to open it directly in the app."

### **Minute 4: Advanced Features (60 seconds)**

> "But here's where it gets interesting—you're not locked into presets. Let's say I want something 'Chill' but with a bit more energy for background work music."

**[Select "Chill" mood, then adjust energy slider to 0.5]**

> "I can use these sliders to fine-tune any audio feature. Watch what happens when I increase the energy while keeping the chill vibe..."

**[Get new recommendations]**

> "Completely different results! This granular control means you can discover music that fits your exact mood at any moment."

### **Minute 5: Technical Highlights & Closing (45 seconds)**

> "From a technical standpoint, this app is built with:
> - **Streamlit** for the web interface
> - **Spotipy** library for seamless Spotify API integration
> - **Audio feature targeting** in the recommendations API
> - **Deployed on Streamlit Community Cloud** for free, making it accessible to anyone

> The app demonstrates real-world API integration, user experience design, and the power of combining music data science with practical applications. Whether you're studying, working out, or just relaxing, this app helps you discover your next favorite song.

> Thank you! Questions?"

### 🎯 **Demo Tips**

- **Practice the timing**: Run through it 2-3 times beforehand
- **Have backup tracks**: Test audio previews ahead of time (not all tracks have them)
- **Prepare for questions**: Common ones include:
  - "How does Spotify's recommendation algorithm work?" (Answer: It uses collaborative filtering + audio analysis)
  - "Can you save playlists?" (Future feature idea!)
  - "What other moods could you add?" (Discuss extensibility)
- **Show enthusiasm**: Your energy will make the demo memorable!
- **Handle failures gracefully**: If API is slow or a preview doesn't load, have a prepared comment like "Sometimes previews aren't available, but the Spotify link always works!"

---

## 📚 How It Works

The app uses Spotify's **Recommendations API** with the following audio features:

- **Valence** (0.0 - 1.0): Musical positiveness. High valence = happy/cheerful, low valence = sad/angry
- **Energy** (0.0 - 1.0): Intensity and activity level. High energy = fast/loud/noisy
- **Danceability** (0.0 - 1.0): How suitable a track is for dancing based on rhythm, tempo, and beat strength
- **Tempo** (BPM): Speed of the track in beats per minute

Each mood preset provides optimal values for these features, which you can then customize using the sliders.

---

## 🛠️ Troubleshooting

### "Spotify credentials not found" Error
- Make sure you've set the environment variables correctly
- Double-check that you copied the Client ID and Secret exactly (no extra spaces)
- If using `.env`, ensure the file is in the same directory as `app.py`

### "No tracks found" Message
- Try adjusting the feature sliders
- Some feature combinations might be too specific—try more moderate values

### Audio Preview Not Available
- Not all Spotify tracks have 30-second previews
- This is a Spotify limitation, not an app issue
- You can still access the full track via the Spotify link

---

## 🎨 Customization Ideas

Want to extend this app? Here are some ideas:

- Add more mood presets
- Include additional audio features (acousticness, instrumentalness, speechiness)
- Allow users to input seed artists or tracks
- Create and save custom playlists to your Spotify account (requires user authentication)
- Add music genre filters
- Implement a "surprise me" random mood generator

---

## 📄 License

This project is open source and available for educational and personal use.

---

## 🙏 Acknowledgments

- **Spotify Web API** for providing the music data and recommendations
- **Streamlit** for making web app development incredibly easy
- **Spotipy** for the excellent Python wrapper around the Spotify API

---

## 📧 Questions or Feedback?

Feel free to reach out or open an issue if you have questions or suggestions for improvement!

---

**Enjoy discovering new music! 🎧✨**
