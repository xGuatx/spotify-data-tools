import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv() 
def transfer_followed_artists(source_sp, target_sp):
    source_artists = []
    offset = 0
    while True:
        artists = source_sp.current_user_followed_artists(limit=50, offset=offset)["artists"]["items"]
        source_artists.extend(artists)
        if len(artists) < 50:
            break
        offset += 50

    target_artists = []
    offset = 0
    while True:
        artists = target_sp.current_user_followed_artists(limit=50, offset=offset)["artists"]["items"]
        target_artists.extend(artists)
        if len(artists) < 50:
            break
        offset += 50

    source_artist_ids = {artist["id"] for artist in source_artists}
    target_artist_ids = {artist["id"] for artist in target_artists}
    artists_to_transfer = list(source_artist_ids - target_artist_ids)

    for artist_id in tqdm(artists_to_transfer, desc="Transferring followed artists"):
        target_sp.user_follow_artists(ids=[artist_id])

    return len(artists_to_transfer)

def transfer_subscribed_podcasts(source_sp, target_sp):
    source_podcasts = []
    offset = 0
    while True:
        podcasts = source_sp.current_user_saved_shows(limit=50, offset=offset)["items"]
        source_podcasts.extend(podcasts)
        if len(podcasts) < 50:
            break
        offset += 50

    target_podcasts = []
    offset = 0
    while True:
        podcasts = target_sp.current_user_saved_shows(limit=50, offset=offset)["items"]
        target_podcasts.extend(podcasts)
        if len(podcasts) < 50:
            break
        offset += 50

    source_podcast_ids = {podcast["show"]["id"] for podcast in source_podcasts}
    target_podcast_ids = {podcast["show"]["id"] for podcast in target_podcasts}
    podcasts_to_transfer = list(source_podcast_ids - target_podcast_ids)

    for podcast_id in tqdm(podcasts_to_transfer, desc="Transferring subscribed podcasts"):
        target_sp.current_user_saved_shows_add(shows=[podcast_id])

    return len(podcasts_to_transfer)

def get_liked_tracks_count(sp):
    return sp.current_user_saved_tracks()["total"]

def check_authorizations(client_id, client_secret, client_username, redirect_uri):
    #redirect_uri = "http://localhost:8080/callback"
    scope = "playlist-read-private,playlist-modify-private,playlist-modify-public,user-library-read,user-library-modify"
    auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope, username=client_username, cache_path=None)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def transfer_playlists(source_sp, target_sp, source_user_id, target_user_id):
    source_playlists = []
    offset = 0
    while True:
        playlists = source_sp.user_playlists(source_user_id, limit=50, offset=offset)["items"]
        source_playlists.extend(playlists)
        if len(playlists) < 50:
            break
        offset += 50

    target_playlists = []
    offset = 0
    while True:
        playlists = target_sp.user_playlists(target_user_id, limit=50, offset=offset)["items"]
        target_playlists.extend(playlists)
        if len(playlists) < 50:
            break
        offset += 50

    target_playlist_names = [playlist["name"] for playlist in target_playlists]
    added_playlists = 0
    for playlist in tqdm(source_playlists, desc="Transferring playlists"):
        if playlist["name"] not in target_playlist_names:
            source_tracks = source_sp.playlist_tracks(playlist["id"])["items"]
            track_uris = []
            for track in source_tracks:
                try:
                    track_uri = track["track"]["uri"]
                    if track_uri.startswith("spotify:track:"):
                        track_uris.append(track_uri)
                except TypeError:
                    pass
            playlist_name = playlist["name"] if playlist["name"] else "Untitled Playlist"
            new_playlist = target_sp.user_playlist_create(target_user_id, playlist_name, public=playlist["public"])
            if track_uris:
                target_sp.playlist_add_items(new_playlist["id"], track_uris)
            added_playlists += 1
    return added_playlists


def transfer_albums(source_sp, target_sp):
    source_albums = []
    offset = 0
    while True:
        albums = source_sp.current_user_saved_albums(limit=50, offset=offset)["items"]
        source_albums.extend(albums)
        if len(albums) < 50:
            break
        offset += 50

    target_albums = []
    offset = 0
    while True:
        albums = target_sp.current_user_saved_albums(limit=50, offset=offset)["items"]
        target_albums.extend(albums)
        if len(albums) < 50:
            break
        offset += 50

    source_album_uris = {album["album"]["uri"] for album in source_albums}
    target_album_uris = {album["album"]["uri"] for album in target_albums}
    added_albums = len(source_album_uris - target_album_uris)
    for album_uri in tqdm(source_album_uris - target_album_uris, desc="Transferring albums"):
        target_sp.current_user_saved_albums_add([album_uri])
    return added_albums

def transfer_liked_tracks(source_sp, target_sp):
    source_tracks = []
    offset = 0
    while True:
        tracks = source_sp.current_user_saved_tracks(limit=50, offset=offset)["items"]
        source_tracks.extend(tracks)
        if len(tracks) < 50:
            break
        offset += 50

    target_tracks = []
    offset = 0
    while True:
        tracks = target_sp.current_user_saved_tracks(limit=50, offset=offset)["items"]
        target_tracks.extend(tracks)
        if len(tracks) < 50:
            break
        offset += 50

    source_track_uris = {track["track"]["uri"] for track in source_tracks}
    target_track_uris = {track["track"]["uri"] for track in target_tracks}
    tracks_to_transfer = list(source_track_uris - target_track_uris)
    added_tracks = len(tracks_to_transfer)

    for track_uri in tqdm(tracks_to_transfer, desc="Transferring liked tracks"):
        target_sp.current_user_saved_tracks_add([track_uri])
    return added_tracks

if __name__ == "__main__":
    # User 1 (Source) - Load from environment
    client_id_1 = os.getenv("SOURCE_CLIENT_ID")
    client_secret_1 = os.getenv("SOURCE_CLIENT_SECRET")
    client_username1 = os.getenv("SOURCE_USERNAME")
    source_redirect_uri = os.getenv("SOURCE_REDIRECT_URI", "http://localhost:8080/callback")

    # User 2 (Target) - Load from environment
    client_id_2 = os.getenv("TARGET_CLIENT_ID")
    client_secret_2 = os.getenv("TARGET_CLIENT_SECRET")
    client_username2 = os.getenv("TARGET_USERNAME")
    target_redirect_uri = os.getenv("TARGET_REDIRECT_URI", "http://localhost:8081/callback")

    # Validate that all required environment variables are set
    if not all([client_id_1, client_secret_1, client_username1, client_id_2, client_secret_2, client_username2]):
        raise ValueError("Missing required environment variables. Please check your .env file.")

    #os.remove(f".cache-{client_username1}")
    #os.remove(f".cache-{client_username2}")
    source_sp = check_authorizations(client_id_1, client_secret_1, client_username1, source_redirect_uri)
    target_sp = check_authorizations(client_id_2, client_secret_2, client_username2, target_redirect_uri)
    input ("entrer pour continuer...")
    source_user_id = source_sp.me()["id"]
    input ("entrer pour continuer...")
    target_user_id = target_sp.me()["id"]
 
    source_tracks_count = get_liked_tracks_count(source_sp)
    target_tracks_count = get_liked_tracks_count(target_sp)

    print(f"Source user has {source_tracks_count} liked tracks.")
    print(f"Target user has {target_tracks_count} liked tracks.")

    added_playlists = transfer_playlists(source_sp, target_sp, source_user_id, target_user_id)
    added_albums = transfer_albums(source_sp, target_sp)
    added_tracks = transfer_liked_tracks(source_sp, target_sp)

    print(f"\nTransferred: {added_playlists} playlists, {added_albums} albums, {added_tracks} liked tracks")