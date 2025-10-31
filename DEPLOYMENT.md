# 🚀 Streamlit Deployment Guide

This guide will help you deploy your Mood2Music app to Streamlit Community Cloud (FREE!)

## Step 1: Go to Streamlit Cloud

Visit: **https://share.streamlit.io**

## Step 2: Sign In with GitHub

Click "Continue with GitHub" and authorize Streamlit to access your repositories.

## Step 3: Deploy New App

1. Click **"New app"** button
2. Select your repository: `bdb-123/enterprise_ai_demo1_websearch`
3. Branch: `main`
4. Main file path: `app.py`

## Step 4: Add Secrets (Optional - for full features)

Click "Advanced settings" → "Secrets" and add:

```toml
SPOTIPY_CLIENT_ID = "your-spotify-client-id"
SPOTIPY_CLIENT_SECRET = "your-spotify-client-secret"
SPOTIPY_REDIRECT_URI = "https://your-actual-app-url.streamlit.app"
```

**Important:** 
- Replace `your-actual-app-url` with your real Streamlit app URL
- Must use `https://` (not `http://`)
- NO trailing slash at the end
- Must match EXACTLY in Spotify Developer Dashboard

**Getting "INVALID_CLIENT" error?** → See [SPOTIFY_OAUTH_SETUP.md](SPOTIFY_OAUTH_SETUP.md) for detailed troubleshooting!

**Note**: The app will work WITHOUT these! You'll just get search-based recommendations instead of personalized ones.

## Step 5: Deploy!

Click **"Deploy!"** and wait 2-3 minutes.

## Your App URL

You'll get a URL like:
```
https://enterprise-ai-demo1-websearch-abc123.streamlit.app
```

## 🎉 Done!

Your app is now live and anyone can access it!

### Features Available:
- ✅ Mood-based music recommendations
- ✅ Audio feature visualization
- ✅ Interactive mood selection
- ✅ Search-based recommendations (no login needed)
- ⚠️ Personal library features (requires Spotify OAuth setup)

## Auto-Deploy

Every time you push to GitHub's `main` branch, Streamlit will automatically redeploy your app! 🔄
