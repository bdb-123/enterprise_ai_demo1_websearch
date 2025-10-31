# 🔐 Spotify OAuth Setup Guide

## Issue: "INVALID_CLIENT" Error

If you're seeing an **INVALID_CLIENT** error when trying to connect your Spotify account, follow this guide to fix it.

## What Causes This Error?

The INVALID_CLIENT error occurs when:
1. ❌ Redirect URI doesn't match between Spotify Dashboard and Streamlit Secrets
2. ❌ Client ID or Client Secret is incorrect
3. ❌ Redirect URI wasn't saved in Spotify Dashboard

## Step-by-Step Fix

### Step 1: Get Your App URL

Your Streamlit app URL should be something like:
```
https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app
```

**Important:** Note the exact URL (copy it from your browser address bar)

### Step 2: Configure Spotify Developer Dashboard

1. **Go to Spotify Developer Dashboard:**
   - Visit: https://developer.spotify.com/dashboard
   - Log in with your Spotify account

2. **Open Your App:**
   - Click on your app (or create a new one if you don't have one)
   - Click "Settings" (top right)

3. **Add Redirect URI:**
   - Scroll to "Redirect URIs" section
   - Click "Edit"
   - Add your Streamlit app URL EXACTLY as shown:
     ```
     https://your-actual-app-url.streamlit.app
     ```
   - ⚠️ **DO NOT add a trailing slash** (`/`)
   - ⚠️ **Must be `https://`** not `http://`
   - Click "Add"
   - Click **"SAVE"** at the bottom (very important!)

4. **Copy Your Credentials:**
   - Client ID: (copy from dashboard)
   - Click "View client secret" and copy it

### Step 3: Configure Streamlit Cloud Secrets

1. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io
   - Find your app
   - Click the ⋮ menu → "Settings"

2. **Add Secrets:**
   - Click on the "Secrets" section
   - Add the following (replace with YOUR values):

   ```toml
   SPOTIPY_CLIENT_ID = "abc123youractualclientid456"
   SPOTIPY_CLIENT_SECRET = "def789youractualsecret012"
   SPOTIPY_REDIRECT_URI = "https://your-actual-app-url.streamlit.app"
   ```

3. **Verify:**
   - ✅ No extra spaces before or after values
   - ✅ Redirect URI matches EXACTLY what you added to Spotify Dashboard
   - ✅ Using `https://` not `http://`
   - ✅ No trailing slash at the end

4. **Save:**
   - Click "Save"
   - Wait for app to restart (30-60 seconds)

### Step 4: Test the Connection

1. Reload your Streamlit app
2. Click "🔐 Connect Spotify" button
3. Click the authorization link
4. You should be redirected to Spotify to approve
5. After approving, you'll be redirected back to your app
6. ✅ Success! You should see "Successfully connected to Spotify!"

## Common Mistakes to Avoid

### ❌ Wrong Redirect URI Format

**WRONG:**
```
http://myapp.streamlit.app/
https://myapp.streamlit.app/  (has trailing slash)
myapp.streamlit.app  (missing https://)
```

**CORRECT:**
```
https://myapp.streamlit.app
```

### ❌ Copy-Paste Errors

- Extra spaces: `" abc123 "` ← wrong
- Wrong quotes: Use straight quotes `"` not curly `""`
- Missing quotes in TOML secrets

### ❌ Forgot to Save

- After adding redirect URI to Spotify Dashboard, you MUST click "Save"
- After editing Streamlit secrets, you MUST click "Save"

## Troubleshooting Checklist

If it still doesn't work, check:

- [ ] Spotify Dashboard shows your redirect URI in the list
- [ ] Redirect URI has NO trailing slash
- [ ] Using `https://` (not `http://`)
- [ ] Client ID matches exactly (check for typos)
- [ ] Client Secret matches exactly
- [ ] Clicked "Save" in both Spotify Dashboard and Streamlit Cloud
- [ ] Waited 60 seconds for Streamlit app to restart after saving secrets
- [ ] Tried clearing browser cache or using incognito mode

## Still Having Issues?

### Check the Error Details

The app now shows a troubleshooting section when you expand "⚙️ Troubleshooting OAuth Connection". It will display:
- Current Redirect URI being used
- Common issues and fixes
- Step-by-step instructions

### Alternative: Use Without OAuth

Good news! The app works perfectly fine **without** OAuth. You'll get:
- ✅ All mood-based recommendations
- ✅ Audio feature customization
- ✅ Search-based song discovery

You just won't have:
- ❌ Personalized recommendations from YOUR library
- ❌ Access to your liked songs
- ❌ Ability to save playlists to your account

To use without OAuth, simply don't click "Connect Spotify" and use the app as-is!

## Example Configuration

Here's a real example (with fake credentials):

**Spotify Dashboard:**
```
App Name: Mood2Music
Client ID: 7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p
Client Secret: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
Redirect URIs:
  - https://mood2music.streamlit.app
```

**Streamlit Cloud Secrets:**
```toml
SPOTIPY_CLIENT_ID = "7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p"
SPOTIPY_CLIENT_SECRET = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
SPOTIPY_REDIRECT_URI = "https://mood2music.streamlit.app"
```

## Quick Reference

| Component | Where to Find | Format |
|-----------|---------------|--------|
| Client ID | Spotify Dashboard | 32-character hex string |
| Client Secret | Spotify Dashboard (click "View") | 32-character hex string |
| Redirect URI | Your Streamlit app URL | `https://app-name.streamlit.app` |

## Need More Help?

Check the Spotify documentation:
- https://developer.spotify.com/documentation/web-api/tutorials/code-flow

Or the Streamlit documentation:
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
