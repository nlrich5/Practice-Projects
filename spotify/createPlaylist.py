import os

from spotifyClient import SpotifyClient

def main():
    spotify_client = SpotifyClient(os.getenv("SPOTIFY_AUTHORIZATION_TOKEN"), os.getenv("SPOTIFY_USER_ID"))

    #get last played tracks
    num_tracks_to_visualize = int(input("How many tacks would you like to visualize? "))
    last_played_tracks = spotify_client.get_last_played_tracks(num_tracks_to_visualize)

    print(f"\nHere are the last {num_tracks_to_visualize} tracks you listened to on Spotify:")
    for index, track in enumerate(last_played_tracks):
        print(f"{index + 1}- {track}")
    
    #choose seed tracks
    indexes = input("\nEnter a list of up to 5 tracks you'd like to use as seeds. Use indexes separated by a space: ")
    indexes = indexes.split()
    seed_tracks = [last_played_tracks[int(index) - 1] for index in indexes]

    #get recommendations
    recommended_tracks = spotify_client.get_track_recommendations(seed_tracks)
    print("\nHere are the recommended tracks which will be included in your new playlist:")
    for index, track in enumerate(recommended_tracks):
        print(f"{index + 1}- {track}")

    #get playlist name from user and create playlist
    playlist_name = input("\nWhat's the playlist name? ")
    playlist = spotify_client.create_playlist(playlist_name)
    print(f"\nPlaylist '{playlist.name}' was created successfully.")

    #populate playlist
    spotify_client.populate_playlist(playlist, recommended_tracks)
    print(f"\nRecommended tracks successfully uploaded to playlist '{playlist.name}'.")

if __name__ == "__main__":
    main()