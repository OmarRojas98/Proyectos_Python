from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import numpy as np
import pandas as pd

load_dotenv()

client_ID = os.getenv("ID_client")
client_Secret_ID = os.getenv("secret_ID_Client")

def get_token():
    auth_string = client_ID + ":" + client_Secret_ID
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_playlist(token, playlist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={playlist_name}&type=playlist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_features(token, songs_id):
    url = f"https://api.spotify.com/v1/audio-features?ids={songs_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

     
def playlist_info(token, name_playlist, file_name):

    playlist_info = search_for_playlist(token, name_playlist)
    playlist_id = playlist_info["playlists"]["items"][0]["id"]
    track_info = get_playlist(token, playlist_id)
    feats = []

    columns = [
        "top",
        "track_name",
        "track_popularity",
        "duration_ms",
        "artist_name",
        "artist_genres",
        "artist_popularity",
        "feats",
        "explicit",
        "album",
        "type",
        "release_date",
        "track_id",
        "artist_id"
    ]
    df_playlist = pd.DataFrame(columns=columns)

    for i, item in enumerate(track_info["tracks"]["items"]):
        track = item["track"]
        data = {
            "top": i + 1,
            "track_name": track["name"],
            "track_popularity": track["popularity"],
            "artist_name": track["artists"][0]["name"],
            "artist_genres": "",
            "duration_ms": track["duration_ms"],
            "artist_popularity": "",
            "feats": "",
            "explicit": track["explicit"],
            "album": track["album"]["name"],
            "type": track["album"]["album_type"],
            "release_date": track["album"]["release_date"],
            "track_id": track["id"],
            "artist_id": track["artists"][0]["id"]
        }

        artist_info = get_artist(token, data["artist_id"])
        data["artist_popularity"] = artist_info["popularity"]

        if len(artist_info["genres"]) == 1:
            data["artist_genres"] = artist_info["genres"][0]
        elif len(artist_info["genres"]) > 1:
            genres = artist_info["genres"]
            data["artist_genres"] = "|".join(genres)
        else:
            data["artist_genres"] = np.nan

        if len(track["artists"]) > 1:
            for j in range(1, len(track["artists"])):
                feats.append(track["artists"][j]["name"])
            data["feats"] = "|".join(feats)
        else:
            data["feats"] = np.nan
        feats = []

        df_playlist = pd.concat([df_playlist, pd.DataFrame([data])], ignore_index=True)

    tracks_id = list(df_playlist["track_id"])
    tracks_id = ",".join(tracks_id)
    df_features = get_features(token, tracks_id)["audio_features"]
    df_features = pd.DataFrame(df_features)
    df_features = df_features[[
        "acousticness", "danceability", "energy", "instrumentalness",
        "liveness", "loudness", "valence", "mode", "tempo", "id"
    ]]
    result_df = pd.merge(df_playlist, df_features, left_on='track_id', right_on='id')
    result_df = result_df.drop('id', axis=1)
    result_df.to_csv(file_name, index=False)
    print(f"El archivo {file_name} fue creado")
    return result_df



def artist_info(token, artist_name):
    # Busca información del artista
    artist_search_result = search_for_artist(token, artist_name)
    artist_id = artist_search_result["artists"]["items"][0]["id"]
    artist_details = get_artist(token, artist_id)
    
    # Prepara el DataFrame para almacenar la información del artista
    columns = [
        "artist_name",
        "artist_popularity",
        "followers",
        "artist_genres",
        "artist_id",
        "external_url"
    ]
    df_artist = pd.DataFrame(columns=columns)
    
    # Obtén los detalles del artista
    data = {
        "artist_name": artist_details["name"],
        "artist_popularity": artist_details["popularity"],
        "followers": artist_details["followers"]["total"],
        "artist_genres": "|".join(artist_details["genres"]) if artist_details["genres"] else np.nan,
        "artist_id": artist_details["id"],
        "external_url": artist_details["external_urls"]["spotify"]
    }

    # Agrega la información al DataFrame
    df_artist = pd.concat([df_artist, pd.DataFrame([data])], ignore_index=True)
    
    # Guarda el DataFrame en un archivo CSV
    #df_artist.to_csv(file_name, index=False)
    #print(f"El archivo {file_name} fue creado")
    return df_artist
