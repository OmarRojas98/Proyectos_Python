from My_Spotify_fuctions import *

def main():
    token = get_token()  # Obtener el token de autenticación
    
    while True:
        print("Elige una opción:")
        print("1. Buscar información de un artista")
        print("2. Buscar información de una playlist")
        print("3. Salir")
        
        choice = input("Ingresa el número de tu elección: ")

        if choice == "1":
            artist_name = input("Ingresa el nombre del artista: ")
            artist = artist_info(token, artist_name)
            print(artist.to_string())
        elif choice == "2":
            playlist_name = input("Ingresa el nombre de la playlist: ")
            file_name = input("Ingresa el nombre del archivo CSV para guardar la información (ejemplo, 'Playlist.csv'): ")
            playlist = playlist_info(token, playlist_name, file_name)
            print(playlist[["top", "track_name", "track_popularity", "artist_name", "artist_popularity", "album"]].to_string())
        elif choice == "3":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    main()
