# 🔧 Redirect URI Configuration Guide

## Current Status

Your app is currently configured with:
```
SPOTIPY_REDIRECT_URI=http://localhost:8501
```

## 📍 What You Need to Do

### For Local Testing
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click on your app
3. Click "Edit Settings"
4. Add these Redirect URIs:
   ```
   http://localhost:8501
   http://localhost:8502
   http://localhost:8503
   http://localhost:8504
   http://localhost:8505
   http://localhost:8506
   ```
   (Streamlit uses different ports, so add multiple for convenience)
5. Click "Save"

### For Streamlit Cloud Deployment

#### Step 1: Deploy First (Get Your URL)
1. Deploy to Streamlit Cloud (without OAuth working yet)
2. Copy your app URL (e.g., `https://your-app-name.streamlit.app`)

#### Step 2: Update Spotify Dashboard
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Add your actual Streamlit URL to Redirect URIs:
   ```
   https://your-app-name.streamlit.app/
   ```
   ⚠️ **Important**: Include the trailing slash `/`

#### Step 3: Update Streamlit Secrets
1. Go to your Streamlit Cloud app settings
2. Click on "Secrets"
3. Update to:
   ```toml
   SPOTIPY_CLIENT_ID = "6cbce910215e41c0bf09c3b36d31a953"
   SPOTIPY_CLIENT_SECRET = "4dae86192be14c51b5b9ccf871c8239b"
   SPOTIPY_REDIRECT_URI = "https://your-app-name.streamlit.app/"
   ```
4. Save (app will restart automatically)

---

## ✅ Verification Checklist

When you open your app, you should see a debug message showing:
```
🔧 Debug: Using redirect URI: `http://localhost:8501`
```

**This MUST exactly match** one of the Redirect URIs in your Spotify Developer Dashboard.

### Common Mistakes to Avoid:
- ❌ Missing trailing slash: `https://app.streamlit.app` vs `https://app.streamlit.app/`
- ❌ HTTP vs HTTPS mismatch
- ❌ Port mismatch (e.g., app uses :8502 but dashboard has :8501)
- ❌ Extra `/callback` path (unless you specifically added it)

### Recommended Setup:
**In Spotify Dashboard**, add BOTH:
```
http://localhost:8501
https://your-app-name.streamlit.app/
```

This allows testing locally AND on Streamlit Cloud!

---

## 🧪 Testing

1. **Open your app**: http://localhost:8506 (or whatever port is shown)
2. **Check the debug message** - it will show the redirect URI being used
3. **Click "Connect Spotify"**
4. **If OAuth works**: You'll be redirected to Spotify, then back to your app
5. **If you get an error**: The redirect URI doesn't match - check Spotify Dashboard

---

## 🚀 For Deployment

When ready to deploy, update `.env` (for local) or Streamlit Secrets (for cloud):

**Local `.env`:**
```
SPOTIPY_REDIRECT_URI=http://localhost:8501
```

**Streamlit Cloud Secrets:**
```toml
SPOTIPY_REDIRECT_URI = "https://your-actual-app-name.streamlit.app/"
```

Then make sure your Spotify Dashboard has BOTH URIs listed!
