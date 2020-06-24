"""
Test your API requests and responses here.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Setup Spotify Credentials
spotify_cid = '06175aec93d14903bad4abb8ea0f16c7'
spotify_secret = '45be25e4ab4a4f7888cd3b18e0d49983'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=spotify_cid, client_secret=spotify_secret))

results = sp.search(q='bach', limit=10)
for idx, track in enumerate(results['tracks']['items']):
    text = f"{idx}: {track['name']}"
    
print(text)