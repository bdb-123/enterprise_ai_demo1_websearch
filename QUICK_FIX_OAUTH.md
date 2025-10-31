# 🚨 QUICK FIX for INVALID_CLIENT Error

## The Problem
You're seeing **INVALID_CLIENT** when clicking "Connect Spotify"

## The Fix (5 minutes)

### 1. Check Your Streamlit App URL
Copy your EXACT app URL from the browser:
```
https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app
```
☝️ This is your REDIRECT_URI

### 2. Add it to Spotify Dashboard

1. Go to: **https://developer.spotify.com/dashboard**
2. Click your app → **Settings**
3. Find "Redirect URIs" → Click **Edit**
4. Paste your URL:
   ```
   https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app
   ```
5. Click **Add**
6. Click **SAVE** ← VERY IMPORTANT!

### 3. Update Streamlit Secrets

1. Go to: **https://share.streamlit.io**
2. Find your app → ⋮ → **Settings** → **Secrets**
3. Make sure SPOTIPY_REDIRECT_URI matches EXACTLY:
   ```toml
   SPOTIPY_REDIRECT_URI = "https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app"
   ```
4. Click **Save**

### 4. Wait & Test
- Wait 60 seconds for restart
- Reload your app
- Click "Connect Spotify" again
- ✅ Should work!

## Common Mistakes

| ❌ Wrong | ✅ Correct |
|---------|-----------|
| `http://...` | `https://...` |
| `https://.../` (trailing slash) | `https://...` (no slash) |
| Forgot to click "Save" | Clicked "Save" |
| Copy-paste with spaces | Clean copy-paste |

## Still Not Working?

Read the full guide: [SPOTIFY_OAUTH_SETUP.md](SPOTIFY_OAUTH_SETUP.md)

Or just use the app WITHOUT OAuth (search-based recommendations work great!)
