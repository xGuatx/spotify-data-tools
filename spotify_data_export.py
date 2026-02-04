import spotipy
from spotipy.oauth2 import SpotifyOAuth

def write_data_to_file(data, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:  # Change 'w' to 'a'
        for key, value in data.items():
            file.write(f"{key}:\n")
            for item in value:
                file.write(f"{item}\n")
            file.write("\n")

def check_authorizations(client_id, client_secret, client_username, redirect_uri):
    scope = "user-top-read,playlist-read-private,playlist-modify-private," + \
            "playlist-modify-public,user-library-read,user-library-modify," + \
            "user-read-recently-played,user-follow-read"
    auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                redirect_uri=redirect_uri, scope=scope,
                                username=client_username, cache_path=None)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def get_top_tracks(sp, limit=50, time_range='long_term'):
    top_tracks = []
    results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    for item in results['items']:
        track = {
            'name': item['name'],
            'id': item['id'],
            'artist': ', '.join([artist['name'] for artist in item['artists']]),
            'album': item['album']['name']
        }
        top_tracks.append(track)
    return top_tracks

def get_top_artists(sp, limit=50, time_range='long_term'):
    top_artists = []
    results = sp.current_user_top_artists(limit=limit, time_range=time_range)
    for item in results['items']:
        artist = {
            'name': item['name'],
            'id': item['id'],
            'genres': item['genres'],
            'popularity': item['popularity']
        }
        top_artists.append(artist)
    return top_artists

def get_recently_played_tracks(sp, limit=50):
    recently_played_tracks = []
    results = sp.current_user_recently_played(limit=limit)
    for item in results['items']:
        track = item['track']
        played_at = item['played_at']  # Date and time of play
        track_info = {
            'name': track['name'],
            'id': track['id'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'played_at': played_at
        }
        recently_played_tracks.append(track_info)
    return recently_played_tracks

def batch_request(sp, request_function, limit=50, *args, **kwargs):
    results = []
    offset = 0
    while True:
        response = request_function(limit=limit, offset=offset, *args, **kwargs)
        items = response['items']
        if not items:
            break
        results.extend(items)
        offset += limit
    return results

def get_liked_tracks_count(sp):
    return sp.current_user_saved_tracks()["total"]

def get_followed_podcasts(sp, limit=50):
    return batch_request(sp, sp.current_user_saved_shows, limit=limit)

def get_saved_albums(sp, limit=50):
    return batch_request(sp, sp.current_user_saved_albums, limit=limit)

def get_saved_tracks(sp, limit=50):
    return batch_request(sp, sp.current_user_saved_tracks, limit=limit)

def count_artist_occurrences(sp):
    saved_tracks = get_saved_tracks(sp, limit=50)  # Adjust limit as needed
    artist_count = {}
    for item in saved_tracks:
        track = item['track']
        for artist in track['artists']:
            artist_name = artist['name']
            artist_count[artist_name] = artist_count.get(artist_name, 0) + 1
    return artist_count

def calculate_listening_time(tracks):
    total_duration_ms = sum(track['duration_ms'] for track in tracks)
    total_duration_min = total_duration_ms / 60000  # Convert milliseconds to minutes
    return total_duration_min

def get_streaming_statistics(sp):
    # Get your top tracks and artists
    top_tracks = get_top_tracks(sp, limit=50, time_range='long_term')
    top_artists = get_top_artists(sp, limit=50, time_range='long_term')

    # Get recently played tracks
    recently_played_tracks = get_recently_played_tracks(sp, limit=50)

    # Calculate total listening time for recently played tracks
    listening_time = calculate_listening_time([track['track'] for track in recently_played_tracks])

    statistics = {
        "Top Tracks": top_tracks,
        "Top Artists": top_artists,
        "Recently Played Tracks": recently_played_tracks,
        "Total Listening Time (Minutes)": listening_time
    }

    return statistics

def rank_tracks_by_playcount(sp):
    recently_played_tracks = get_recently_played_tracks(sp, limit=50)
    track_playcount = {}
    for item in recently_played_tracks:
        track_id = item['track']['id']
        track_name = item['track']['name']
        track_playcount[track_name] = track_playcount.get(track_name, 0) + 1
    sorted_tracks = sorted(track_playcount.items(), key=lambda x: x[1], reverse=True)
    return sorted_tracks


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # User credentials from environment
    client_id_1 = os.getenv("SOURCE_CLIENT_ID")
    client_secret_1 = os.getenv("SOURCE_CLIENT_SECRET")
    client_username1 = os.getenv("SOURCE_USERNAME")
    redirect_uri = os.getenv("SOURCE_REDIRECT_URI", "http://localhost:8080/callback")

    # Validate required variables
    if not all([client_id_1, client_secret_1, client_username1]):
        raise ValueError("Missing required environment variables. Please check your .env file.")

    source_sp = check_authorizations(client_id_1, client_secret_1, client_username1, redirect_uri)
    source_user_id = source_sp.me()["id"]

    data_file = 'all_spotify_data.txt'

    # Clear file at the beginning
    open(data_file, 'w').close()

    # Write top tracks to file
    top_tracks = get_top_tracks(source_sp)
    write_data_to_file({'Top Tracks': top_tracks}, data_file)

    # Write top artists to file
    top_artists = get_top_artists(source_sp)
    write_data_to_file({'Top Artists': top_artists}, data_file)

    # Write recently played tracks to file
    recently_played_tracks = get_recently_played_tracks(source_sp)
    write_data_to_file({'Recently Played Tracks': recently_played_tracks}, data_file)

    # Write followed podcasts to file
    followed_podcasts = get_followed_podcasts(source_sp)
    write_data_to_file({'Followed Podcasts': followed_podcasts}, data_file)

    # Write saved albums to file
    saved_albums = get_saved_albums(source_sp)
    write_data_to_file({'Saved Albums': saved_albums}, data_file)

    # Write liked tracks to file
    saved_tracks = get_saved_tracks(source_sp)
    write_data_to_file({'Saved Tracks': saved_tracks}, data_file)

    # Write artist occurrences to file
    artist_counts = count_artist_occurrences(source_sp)
    write_data_to_file({'Artist Occurrences': artist_counts}, data_file)

    # Write track play count rankings to file
    track_rankings = rank_tracks_by_playcount(source_sp)
    write_data_to_file({'Track Play Count Rankings': track_rankings}, data_file)

    print(f"\nData export completed! Check {data_file} for results.")
   