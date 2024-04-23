import json

class Track:

    def __init__(self, name, track_id, artist):
        self.name = name
        self.track_id = track_id
        self.artist = artist

    def create_spotify_uri(self):
        return f"spotify:track:{self.track_id}"
    
    def __str__(self):
        return self.name + " by " + self.artist
    
    def __json__(self):
        return json.dumps(self, default=lambda o: o.__dict__)