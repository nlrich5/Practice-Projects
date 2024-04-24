import json
from flask import Flask, redirect, request, jsonify, session, render_template
from datetime import datetime, timedelta
import requests
import urllib.parse
from track import Track
from playlistMaker import PlaylistMaker

app = Flask(__name__)
app.secret_key = '345e42a3-51b0-437a-1230-1f4e443a2a3e'

CLIENT_ID = '661ed0776f844cbfa9956fbbe7a64337'
CLIENT_SECRET = '65684616b17b4a4db5dc35d490089e6e'
REDIRECT_URI = 'http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

USER_ID = "nlrich175"

songs = []

@app.route('/')
def index():
    global songs
    songs = []
    return render_template('index.html')

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': False
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(
            TOKEN_URL,
            data=req_body
        )
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return render_template('main-menu.html')
    
@app.route('/op1', methods=['POST', 'GET'])
def option1():
    return render_template('ask-for-playlist-op1.html')

@app.route('/op2', methods=['POST', 'GET'])
def option2():
    return render_template('ask-for-playlist-op2.html')
    
@app.route('/ask-for-playlist-op1', methods=['POST', 'GET'])
def ask_for_playlist():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    session['search_playlist'] = request.form.get('search')
    
    return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    global songs

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)

    playlists = response.json()
    print(session['search_playlist'])
    for item in playlists['items']:
        if item['name'] == session['search_playlist']:
            tracks_url = item['tracks']['href']
            response2 = requests.get(tracks_url, headers=headers)
            tracks = response2.json()
            songs = [Track(track["track"]["name"], track["track"]["id"], track["track"]["artists"][0]["name"]) for track in tracks["items"]]
            
            return render_template('songs-in-playlist.html', data=songs)
        
    return jsonify(playlists)

@app.route('/get_recs', methods=['POST', 'GET'])
def get_recs():
    global songs
    plMaker = PlaylistMaker(session['access_token'], USER_ID)
    indexes = request.form.get('seeds')
    indexes = indexes.split()
    seed_tracks = [songs[int(index) - 1] for index in indexes]
    seed_tracks_url = ""
    for seed_track in seed_tracks:
        seed_tracks_url += seed_track.track_id + ","
    seed_tracks_url = seed_tracks_url[:-1]
    url = f"https://api.spotify.com/v1/recommendations?seed_tracks={seed_tracks_url}&limit={50}"
    
    rec_response = requests.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {session['access_token']}"
        }
    )
    rec_json = rec_response.json()
    rec_tracks = [Track(rec_track["name"], rec_track["id"], rec_track["artists"][0]["name"]) for rec_track in rec_json["tracks"]]
    print("\nHere are the recommended tracks which will be included in your new playlist:")
    for index, track in enumerate(rec_tracks):
        print(f"{index + 1} - {track}")
    
    playlist = plMaker.create_playlist(name=f"{session['search_playlist']} (Expanded)")
    playlist_json = plMaker.populate_playlist(playlist=playlist, tracks=rec_tracks)

    return render_template('rec-songs.html', data=rec_tracks)

@app.route('/ask-for-playlist-op2', methods=['POST', 'GET'])
def ask_for_playlist_op2():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    session['search_playlist'] = request.form.get('search')
    
    return redirect('/playlists-op2')

@app.route('/playlists-op2')
def get_playlists_op2():
    global songs

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)

    playlists = response.json()
    print(session['search_playlist'])
    for item in playlists['items']:
        if item['name'] == session['search_playlist']:
            tracks_url = item['tracks']['href']
            response2 = requests.get(tracks_url, headers=headers)
            tracks = response2.json()
            songs = [Track(track["track"]["name"], track["track"]["id"], track["track"]["artists"][0]["name"]) for track in tracks["items"]]
            
            return render_template('songs-in-playlist-op2.html', data=songs)
        
    return jsonify(playlists)

@app.route('/get-recs-op2', methods=['POST', 'GET'])
def get_recs_op2():
    global songs

    plMaker = PlaylistMaker(session['access_token'], USER_ID)
    songs_str = []
    playlist = plMaker.create_playlist(name=f"{session['search_playlist']} (Expanded)")

    for song in songs:
        url = f"https://api.spotify.com/v1/recommendations?seed_tracks={song.track_id}&limit={3}"
        
        rec_response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {session['access_token']}"
            }
        )
        rec_json = rec_response.json()

        rec_tracks = [Track(rec_track["name"], rec_track["id"], rec_track["artists"][0]["name"]) for rec_track in rec_json["tracks"]]
        playlist_json = plMaker.populate_playlist(playlist=playlist, tracks=rec_tracks)
        for song in rec_tracks:
            songs_str.append(f"{song}")

    return render_template('rec-songs.html', data=songs_str)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant-type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlists')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)