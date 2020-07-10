import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
cid = '06175aec93d14903bad4abb8ea0f16c7'
secret = '45be25e4ab4a4f7888cd3b18e0d49983'

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)

# * the below code works, to return a list of the names of all the albums released by the artist ‘Birdy’:
# birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
# spotify = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# results = spotify.artist_albums(birdy_uri, album_type='album')
# albums = results['items']
# while results['next']:
#     results = spotify.next(results)
#     albums.extend(results['items'])

# for album in albums:
#     print(album['name'])

# * the below code works, to print 30 second samples and cover art for the top 10 tracks for Led Zeppelin:
# lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

# spotify = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
# results = spotify.artist_top_tracks(lz_uri)

# for track in results['tracks'][:10]:
#     print('track    : ' + track['name'])
#     print('audio    : ' + track['preview_url'])
#     print('cover art: ' + track['album']['images'][0]['url'])
#     print()
# test