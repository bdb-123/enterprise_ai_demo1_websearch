# Streamlit Cloud Secrets Setup

## 🔑 Add OpenAI API Key to Streamlit Cloud

For the GPT-powered chatbot to work on your deployed app, you need to add your OpenAI API key to Streamlit Cloud secrets.

### Steps:

1. **Go to Streamlit Cloud Dashboard**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub

2. **Navigate to Your App Settings**
   - Click on your app: `enterprise_ai_demo1_websearch`
   - Click the **⚙️ Settings** button (three dots menu)

3. **Add Secrets**
   - Click on **Secrets** in the left sidebar
   - Add the following in the secrets editor:

```toml
# Copy these values from your .env file
OPENAI_API_KEY = "sk-proj-your-actual-openai-key-here"

SPOTIPY_CLIENT_ID = "your-spotify-client-id"
SPOTIPY_CLIENT_SECRET = "your-spotify-client-secret"
SPOTIPY_REDIRECT_URI = "https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app"
```

   **Note**: Replace the placeholder values with your actual keys from `.env` file

4. **Save**
   - Click **Save**
   - Your app will automatically restart with the new secrets

## ✅ Verification

After adding secrets:
1. Wait 30 seconds for app to restart
2. Go to your app: https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app
3. Try the chatbot with: "I wanna cry"
4. You should see GPT understanding your request!

## 🔒 Security Note

- Never commit `secrets.toml` to git (already in `.gitignore`)
- Streamlit Cloud secrets are encrypted and secure
- Only your app can access these secrets

## 🐛 Troubleshooting

If GPT isn't working:
- Check secrets are saved correctly in Streamlit Cloud
- Look for error message: "AI processing temporarily unavailable"
- If you see this, the app falls back to keyword matching
- Verify your OpenAI API key is valid at: https://platform.openai.com/api-keys

## 💡 Local Development

For local testing, the app uses `.env` file (already configured).
For deployed app, it uses Streamlit Cloud secrets (you need to add manually).
