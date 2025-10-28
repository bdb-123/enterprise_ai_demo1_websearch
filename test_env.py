import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

print("Client ID:", client_id)
if client_secret:
    print("Client Secret:", client_secret[:5] + "...")
else:
    print("Client Secret: Not found")

if client_id and client_secret:
    print("\n✅ Both credentials loaded successfully!")
else:
    print("\n❌ Credentials not found - check your .env file")
