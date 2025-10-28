# 🎯 Spotify Developer Dashboard Setup - Quick Reference

## Step-by-Step Instructions

### 1. Go to Spotify Developer Dashboard
🔗 https://developer.spotify.com/dashboard

### 2. Open Your App
- Click on your app: **"Mood Track Recommender"** (or whatever you named it)

### 3. Click "Edit Settings"
- Look for the "Edit Settings" button (top right)

### 4. Add Redirect URIs

Scroll down to the **"Redirect URIs"** section and add:

#### For Local Testing:
```
http://localhost:8501/callback
```

#### For Streamlit Cloud Production:
```
https://YOUR-APP-NAME.streamlit.app/callback
```

**⚠️ IMPORTANT:**
- Replace `YOUR-APP-NAME` with your actual Streamlit app URL
- Include `/callback` at the end
- Match the exact format (http vs https, trailing slash, etc.)

### 5. Click "Add" for Each URI

After typing each URI, click the "Add" button next to it.

### 6. Click "Save" at the Bottom

Scroll to the bottom and click the green "Save" button.

---

## 📋 Your Redirect URIs Should Look Like:

```
✅ http://localhost:8501/callback
✅ https://your-actual-app-name.streamlit.app/callback
```

---

## 🔄 After Deployment to Streamlit Cloud

Once you deploy and get your actual Streamlit URL:

1. **Copy the URL** (e.g., `https://my-spotify-app.streamlit.app`)
2. **Come back to this dashboard**
3. **Click "Edit Settings"** again
4. **Update** the second URI to use your actual app name
5. **Save**

---

## ✅ Verification

Your app will show a debug message (in local mode):
```
🔧 Debug: Using redirect URI: http://localhost:8501/callback
```

This MUST exactly match what you added in the Spotify Dashboard!

---

## 🚀 For Streamlit Cloud Secrets

When deploying, add these secrets:

```toml
SPOTIPY_CLIENT_ID = "6cbce910215e41c0bf09c3b36d31a953"
SPOTIPY_CLIENT_SECRET = "4dae86192be14c51b5b9ccf871c8239b"
SPOTIPY_REDIRECT_URI = "https://your-actual-app-name.streamlit.app/callback"
```

Replace `your-actual-app-name` with your real Streamlit URL!

---

## ❌ Common Mistakes

- Missing `/callback` path
- Using `http://` for Streamlit Cloud (should be `https://`)
- Forgetting to click "Add" before clicking "Save"
- Typo in the app name
- Extra spaces before or after the URI

---

## ✨ Quick Test

After setting up:

1. Open your local app: http://localhost:8506 (or current port)
2. Check the debug message shows correct URI
3. Click "🔐 Connect Spotify"
4. Should redirect to Spotify login
5. After login, should redirect back to your app
6. Profile picture and name should appear in sidebar

If it fails: Double-check the URIs match EXACTLY! ✏️
