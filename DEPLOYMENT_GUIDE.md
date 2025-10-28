# 🚀 Streamlit Cloud Deployment Guide for Spotify OAuth

## Overview
This guide shows you how to deploy your Spotify Mood Recommender to Streamlit Cloud with OAuth login enabled.

---

## 📋 Pre-Deployment Checklist

### 1. **Update Spotify Developer App Settings**

Before deploying, you need to configure your Spotify app for production:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click on your app
3. Click **"Edit Settings"**
4. In the **"Redirect URIs"** section, add:
   ```
   https://YOUR-APP-NAME.streamlit.app/
   ```
   ⚠️ **Replace `YOUR-APP-NAME` with your actual Streamlit app URL** (you'll get this after first deployment)
   
5. Click **"Add"** then **"Save"**

---

## 🌐 Deploy to Streamlit Cloud

### Step 1: Push Code to GitHub
Your code is already committed. Just make sure the latest changes are pushed:

```bash
git add app.py .gitignore
git commit -m "Update OAuth for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Create Streamlit Cloud App

1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Configure:
   - **Repository**: `bdb-123/enterprise_ai_demo1_websearch`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (optional): Choose a custom name or use auto-generated

### Step 3: Add Secrets

Click **"Advanced settings"** → **"Secrets"**, then paste:

```toml
SPOTIPY_CLIENT_ID = "6cbce910215e41c0bf09c3b36d31a953"
SPOTIPY_CLIENT_SECRET = "4dae86192be14c51b5b9ccf871c8239b"
SPOTIPY_REDIRECT_URI = "https://YOUR-APP-NAME.streamlit.app/"
```

⚠️ **IMPORTANT**: Replace `YOUR-APP-NAME` with the actual URL Streamlit gives you!

### Step 4: Deploy

1. Click **"Deploy!"**
2. Wait 1-2 minutes for deployment
3. Copy your app URL (e.g., `https://your-app-name.streamlit.app`)

---

## 🔧 Post-Deployment Configuration

### Update Spotify Redirect URI

Now that you have your actual Streamlit app URL:

1. Go back to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Edit your app settings
3. **Update the Redirect URI** to match your actual Streamlit URL:
   ```
   https://your-actual-app-name.streamlit.app/
   ```
4. Make sure to include the trailing slash `/`
5. Save

### Update Streamlit Secrets

1. Go to your Streamlit Cloud app settings
2. Navigate to **Secrets**
3. Update `SPOTIPY_REDIRECT_URI` to your actual app URL:
   ```toml
   SPOTIPY_REDIRECT_URI = "https://your-actual-app-name.streamlit.app/"
   ```
4. Save (app will automatically restart)

---

## ✅ Test OAuth Login

1. Open your deployed app
2. Click **"🔐 Connect Spotify"**
3. You'll be redirected to Spotify login
4. After authorizing, you'll be redirected back to your app
5. Your Liked Songs will be loaded automatically!

---

## 🔍 Troubleshooting

### "Invalid redirect URI" error
- Make sure the redirect URI in Spotify Developer Dashboard **exactly matches** your Streamlit app URL
- Include or exclude the trailing slash `/` consistently
- Common mistake: forgetting to update after getting your actual Streamlit URL

### OAuth not working locally
For local development, keep:
```
SPOTIPY_REDIRECT_URI=http://localhost:8501
```
And add `http://localhost:8501` to your Spotify app's Redirect URIs

### "No cached token" or login loop
- Clear cache: Delete `.cache_streamlit` file (Streamlit Cloud does this automatically)
- Ensure `show_dialog=True` in the OAuth config (already set)

### App shows "Not logged in"
- Check that all three secrets are set in Streamlit Cloud
- Verify the redirect URI matches exactly
- Try refreshing the page after authorization

---

## 📝 Notes

- **OAuth flow works differently in production**: The callback URL must match exactly
- **Secrets are encrypted** in Streamlit Cloud - safe to use
- **Cache is temporary** - users need to re-login after cache expires
- **No database needed** - OAuth tokens are cached per session

---

## 🎉 Your Deployment Checklist

- [ ] Push latest code to GitHub
- [ ] Create Streamlit Cloud app
- [ ] Add secrets (Client ID, Client Secret, Redirect URI placeholder)
- [ ] Deploy and get actual app URL
- [ ] Update Spotify Developer Dashboard with actual redirect URI
- [ ] Update Streamlit secrets with actual redirect URI
- [ ] Test OAuth login flow
- [ ] Share your app URL! 🎵

---

**Once deployed, your app will be live at:**
```
https://your-app-name.streamlit.app
```

Users can click "Connect Spotify" to use their Liked Songs for personalized recommendations!
