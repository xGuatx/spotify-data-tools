import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load credentials from environment
SPOTIFY_CLIENT_ID = os.getenv('SOURCE_CLIENT_ID')  # Reusing SOURCE_CLIENT_ID from .env
SPOTIFY_CLIENT_SECRET = os.getenv('SOURCE_CLIENT_SECRET')
SPOTIFY_USER_ID = os.getenv('SOURCE_USERNAME')
JELLYFIN_API_KEY = os.getenv('JELLYFIN_API_KEY')
JELLYFIN_SERVER_URL = os.getenv('JELLYFIN_URL')

# Validate required variables
if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, JELLYFIN_API_KEY, JELLYFIN_SERVER_URL]):
    raise ValueError("Missing required environment variables for Jellyfin integration. Check your .env file.")

# Authentification à l'API Spotify
def get_spotify_token(client_id, client_secret):
    # Endpoint pour la demande de token
    token_url = "https://accounts.spotify.com/api/token"

    # Paramètres de la demande pour obtenir un token d'accès
    payload = {
        'grant_type': 'client_credentials'
    }

    # Authentification avec les identifiants de l'application Spotify
    auth = HTTPBasicAuth(client_id, client_secret)

    # Faire la demande de token
    response = requests.post(token_url, data=payload, auth=auth)

    # Vérifier si la demande a réussi
    if response.status_code == 200:
        # Extraire le token d'accès de la réponse
        token = response.json()['access_token']
        return token
    else:
        # Gestion des erreurs
        raise Exception(f"Failed to obtain token from Spotify, status code: {response.status_code}")

# Utilisation de la fonction
# spotify_token = get_spotify_token('votre_client_id', 'votre_client_secret')
# print(spotify_token)

# Récupérer les playlists de l'utilisateur Spotify
def get_spotify_playlists(access_token, user_id):
    # L'endpoint pour les playlists d'un utilisateur Spotify
    playlists_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

    # Les entêtes pour la requête avec le token d'accès
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Liste pour stocker les playlists
    playlists = []

    # Faire la requête à l'API
    response = requests.get(playlists_url, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Extraire les playlists de la réponse
        data = response.json()
        playlists.extend(data['items'])
        
        # Paginer si plus de playlists sont disponibles
        while data['next']:
            response = requests.get(data['next'], headers=headers)
            data = response.json()
            playlists.extend(data['items'])

        return playlists
    else:
        # Gestion des erreurs
        raise Exception(f"Failed to obtain playlists from Spotify, status code: {response.status_code}")

# Utilisation de la fonction
# spotify_access_token = 'votre_token_d'accès_spotify'
# spotify_user_id = 'huglofficiel67'
# user_playlists = get_spotify_playlists(spotify_access_token, spotify_user_id)
# for playlist in user_playlists:
#     print(playlist['name'])
# Récupérer les détails de la playlist Spotify

def get_playlist_tracks(access_token, playlist_id):
    # Endpoint pour obtenir les pistes d'une playlist spécifique sur Spotify
    tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Les entêtes pour la requête avec le token d'accès
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Liste pour stocker les pistes de la playlist
    playlist_tracks = []

    # Paginer à travers les résultats car une playlist peut contenir un grand nombre de pistes
    while tracks_url:
        # Faire la requête à l'API
        response = requests.get(tracks_url, headers=headers)
        
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            data = response.json()
            tracks_url = data['next']  # Lien pour la page suivante
            items = data['items']
            
            # Extraire les pistes et les ajouter à la liste
            for item in items:
                track = item['track']
                playlist_tracks.append({
                    'name': track['name'],
                    'artist': ', '.join(artist['name'] for artist in track['artists']),
                    'album': track['album']['name'],
                    'uri': track['uri']  # URI Spotify de la piste
                })
        else:
            raise Exception(f"Failed to obtain playlist tracks from Spotify, status code: {response.status_code}")

    return playlist_tracks

# Utilisation de la fonction
# spotify_access_token = 'votre_token_d'accès_spotify'
# playlist_id = 'votre_playlist_id'
# tracks = get_playlist_tracks(spotify_access_token, playlist_id)
# for track in tracks:
#     print(track['name'], '-', track['artist'])

# Authentification à l'API Jellyfin
def get_jellyfin_session(server_url, api_key):
    # Endpoint pour l'authentification Jellyfin
    auth_url = f"{server_url}/Users/AuthenticateByName"

    # Données pour l'authentification
    auth_data = {
        'Username': 'votre_nom_utilisateur',
        'Pw': 'votre_mot_de_passe'
    }

    # Entêtes de la requête, incluant la clé API
    headers = {
        'X-Emby-Token': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Faire la requête POST pour authentifier l'utilisateur
    response = requests.post(auth_url, json=auth_data, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Extraire le token d'accès de la réponse
        data = response.json()
        user_token = data['AccessToken']
        return user_token
    else:
        # Gestion des erreurs
        raise Exception(f"Failed to authenticate with Jellyfin, status code: {response.status_code}")

# Utilisation de la fonction
# jellyfin_api_key = 'votre_api_key_jellyfin'
# jellyfin_server_url = 'https://your-jellyfin-server.example.com'
# jellyfin_user_token = get_jellyfin_session(jellyfin_server_url, jellyfin_api_key)
# print(jellyfin_user_token)
# Créer une playlist dans Jellyfin

def create_jellyfin_playlist(api_key, server_url, user_id, playlist_name):
    # Endpoint pour la création d'une playlist dans Jellyfin
    create_playlist_url = f"{server_url}/Playlists"

    # Données nécessaires pour créer la playlist
    data = {
        'Name': playlist_name,
        'Ids': [],  # IDs des éléments à ajouter à la playlist, vide pour le moment
        'UserId': user_id,
        'MediaType': 'Audio'  # Type de média, 'Audio' pour une playlist de musique
    }

    # Entêtes pour la requête, incluant la clé API
    headers = {
        'X-Emby-Token': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Faire la requête POST pour créer la playlist
    response = requests.post(create_playlist_url, json=data, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Extraire l'ID de la playlist créée de la réponse
        playlist_id = response.json()['Id']
        return playlist_id
    else:
        # Gestion des erreurs
        raise Exception(f"Failed to create playlist in Jellyfin, status code: {response.status_code}")

# Utilisation de la fonction
# jellyfin_api_key = 'votre_api_key_jellyfin'
# jellyfin_server_url = 'https://your-jellyfin-server.example.com'
# jellyfin_user_id = 'votre_user_id_jellyfin'
# playlist_name = 'Ma Nouvelle Playlist'
# new_playlist_id = create_jellyfin_playlist(jellyfin_api_key, jellyfin_server_url, jellyfin_user_id, playlist_name)
# print(new_playlist_id)

def get_saved_tracks(access_token):
    # L'endpoint Spotify pour les morceaux sauvegardés dans la bibliothèque de l'utilisateur
    saved_tracks_url = "https://api.spotify.com/v1/me/tracks"

    # Les entêtes pour la requête avec le token d'accès
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Liste pour stocker les morceaux sauvegardés
    saved_tracks = []

    # Faire la requête à l'API
    response = requests.get(saved_tracks_url, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Extraire les morceaux sauvegardés de la réponse
        data = response.json()
        saved_tracks.extend(data['items'])
        
        # Paginer si plus de morceaux sont disponibles
        while data['next']:
            response = requests.get(data['next'], headers=headers)
            data = response.json()
            saved_tracks.extend(data['items'])
            
        # Retourner uniquement les informations pertinentes des morceaux sauvegardés
        return [{'name': track['track']['name'], 'artist': track['track']['artists'][0]['name'], 'album': track['track']['album']['name']} for track in saved_tracks]
    else:
        # Gestion des erreurs
        raise Exception(f"Failed to obtain saved tracks from Spotify, status code: {response.status_code}")

# Utilisation de la fonction
# spotify_access_token = 'votre_token_d'accès_spotify'
# liked_tracks = get_saved_tracks(spotify_access_token)
# for track in liked_tracks:
#     print(f"{track['name']} by {track['artist']} from the album {track['album']}")

# Ajouter des pistes à une playlist dans Jellyfin
def add_tracks_to_jellyfin_playlist(api_key, server_url, playlist_id, track_ids):
    # Endpoint pour ajouter des pistes à une playlist dans Jellyfin
    add_to_playlist_url = f"{server_url}/Playlists/{playlist_id}/Items"

    # Paramètres pour l'ajout des pistes à la playlist
    params = {
        'Ids': ','.join(track_ids)  # Les ID des pistes à ajouter, séparés par des virgules
    }

    # Entêtes pour la requête, incluant la clé API
    headers = {
        'X-Emby-Token': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Faire la requête POST pour ajouter les pistes
    response = requests.post(add_to_playlist_url, params=params, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 204:
        print("Tracks added to playlist successfully.")
    else:
        # Gestion des erreurs
        raise Exception(f"Failed to add tracks to playlist in Jellyfin, status code: {response.status_code}")

# Utilisation de la fonction
# jellyfin_api_key = 'votre_api_key_jellyfin'
# jellyfin_server_url = 'https://your-jellyfin-server.example.com'
# playlist_id = 'l'ID_de_votre_playlist_jellyfin'
# track_ids = ['l'ID_de_la_première_piste', 'l'ID_de_la_deuxième_piste', ...]
# add_tracks_to_jellyfin_playlist(jellyfin_api_key, jellyfin_server_url, playlist_id, track_ids)

# Fonction principale orchestrant le processus de transfert
def transfer_playlists():
    spotify_token = get_spotify_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    playlists = get_spotify_playlists(spotify_token, SPOTIFY_USER_ID)
    
    jellyfin_session = get_jellyfin_session(JELLYFIN_API_KEY)
    
    for playlist in playlists:
        tracks = get_playlist_tracks(spotify_token, playlist['id'])
        jellyfin_playlist_id = create_jellyfin_playlist(jellyfin_session, playlist['name'])
        add_tracks_to_jellyfin_playlist(jellyfin_session, jellyfin_playlist_id, tracks)

# Point d'entrée du script
if __name__ == "__main__":
    transfer_playlists()