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

# def get_songs_by_composer(response, fb_id):
#     # WIP
#     pass

# try:
#     if 'Baroque_Composer:Baroque_Composer' in response['entities']:
#         composer_name = response['entities']["Baroque_Composer:Baroque_Composer"][0]['name']                    
#     elif 'Classical_Composer:Classical_Composer' in response['entities']:
#         composer_name = response['entities']["Classical_Composer:Classical_Composer"][0]['name']  
#     elif 'Romantic_Composer:Romantic_Composer' in response['entities']:
#         composer_name = response['entities']["Romantic_Composer:Romantic_Composer"][0]['name']
#     elif 'Modern_Composer:Modern_Composer' in response['entities']:
#         composer_name = response['entities']["Modern_Composer:Modern_Composer"][0]['name']

#     results = sp.search(composer_name, limit=10)
#     for idx, track in enumerate(results['tracks']['items']):
#         print(idx, track['name'])
#         text = track['name']
# except Exception as e:
#     print("EXCEPTION:", e)
#     text = "Sorry, we are still working on this feature. Try again next time!"