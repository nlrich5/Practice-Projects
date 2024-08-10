import requests
import json
from playlist import Playlist

CLIENT_ID = '661ed0776f844cbfa9956fbbe7a64337'
CLIENT_SECRET = '65684616b17b4a4db5dc35d490089e6e'
REDIRECT_URI = 'http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

class PlaylistMaker:

    def __init__(self, access_token, user_id):
        self.access_token = access_token
        self.user_id = user_id

    def _place_get_api_request(self, url):
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        return response

    def _place_post_api_request(self, url, data):
        response = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        )
        return response

    def create_playlist(self, name):
        data = json.dumps({
            "name": name,
            "description": "Recommended songs",
            "public": True
        })
        url = f"{API_BASE_URL}users/{self.user_id}/playlists"
        response = self._place_post_api_request(url, data)
        response_json = response.json()

        playlist_id = response_json["id"]
        playlist = Playlist(name, playlist_id)
        return playlist

    def populate_playlist(self, playlist, tracks):
        track_uris = [track.create_spotify_uri() for track in tracks]
        data = json.dumps(track_uris)
        url = f"https://api.spotify.com/v1/playlists/{playlist.id}/tracks"
        response = self._place_post_api_request(url, data)
        response_json = response.json()
        return response_json
    
    def sort_songs(self, songs):
        genres = {}
        for song in songs:
            string = ''
            url = f"https://api.spotify.com/v1/audio-features/{song.track_id}"
            response = self._place_get_api_request(url)
            response_json = response.json()

            if response_json['acousticness'] < 0.33333:
                string = string + 'L'
            elif response_json['acousticness'] < 0.66667:
                string = string + 'M'
            else:
                string = string + 'H'

            if response_json['danceability'] < 0.33333:
                string = string + 'L'
            elif response_json['danceability'] < 0.66667:
                string = string + 'M'
            else:
                string = string + 'H'

            if response_json['energy'] < 0.33333:
                string = string + 'L'
            elif response_json['energy'] < 0.66667:
                string = string + 'M'
            else:
                string = string + 'H'

            if response_json['instrumentalness'] <= 0.5:
                string = string + 'L'
            else:
                string = string + 'H'

            if response_json['speechiness'] < 0.33333:
                string = string + 'L'
            elif response_json['speechiness'] < 0.66667:
                string = string + 'M'
            else:
                string = string + 'H'

            if response_json['tempo'] < 60:
                string = string + 'L'
            elif response_json['tempo'] < 100:
                string = string + 'M'
            else:
                string = string + 'H'

            if response_json['valence'] < 0.33333:
                string = string + 'L'
            elif response_json['valence'] < 0.66667:
                string = string + 'M'
            else:
                string = string + 'H'

            if string in genres.keys():
                curr_genres = []
                curr_genres = genres.get(string)
                curr_genres.append(song)
                genres[string] = curr_genres
            else:
                genres[string] = [song]

        return genres
    
    def merge_playlists(self, genre_dict):
        # order of merge: acousticness, speechiness, instrumentalness, danceability, energy, valence, tempo
        needs_merge = []
        for key, value in genre_dict.items():
            if len(value) < 4:
                needs_merge.append(key)

        temp_dict = {}
        for playlist in needs_merge:
            temp_name = playlist[2] + playlist[5] + playlist[6]
            if temp_name in temp_dict.keys():
                temp = []
                temp = temp_dict.get(temp_name)
                temp.append(playlist)
                temp_dict[temp_name] = temp
            else:
                temp_dict[temp_name] = [playlist]
        
        for key2, value2 in temp_dict.items():
            playlist_songs = []
            for playlist in value2:
                temp = []
                temp = genre_dict.get(playlist)
                for song in temp:
                    playlist_songs.append(song)
                genre_dict.pop(playlist)

            genre_dict[key2] = playlist_songs

        return genre_dict