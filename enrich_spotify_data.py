import os
import django
import time
import requests

import info

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotify_analytics.settings')
django.setup()

from analytics.models import Track, Artist, Genre

CLIENT_ID = info.CLIENT_ID
CLIENT_SECRET = info.CLIENT_SECRET


def get_new_token():
    url = "https://accounts.spotify.com/api/token"
    response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(CLIENT_ID, CLIENT_SECRET))
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Ошибка токена: {response.text}")


def enrich_tracks(limit=100):
    empty_tracks = list(Track.objects.filter(title__isnull=True)[:limit])

    if not empty_tracks:
        print("База полностью готова.")
        return

    print(f"🔍 Найдено {len(empty_tracks)} пустых треков")
    token = get_new_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for idx, track_db in enumerate(empty_tracks, 1):
        try:
            track_url = f"https://api.spotify.com/v1/tracks/{track_db.id}"
            response = requests.get(track_url, headers=headers)

            if response.status_code == 401:
                token = get_new_token()
                headers["Authorization"] = f"Bearer {token}"
                response = requests.get(track_url, headers=headers)

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"Spotify просит подождать {retry_after} сек...")
                time.sleep(retry_after)
                response = requests.get(track_url, headers=headers)

            if response.status_code != 200:
                if response.status_code == 404:
                    track_db.is_available = False
                    track_db.save()
                else:
                    print(f"Ошибка {response.status_code} на треке {track_db.id}")
                continue

            t_info = response.json()
            track_db.title = t_info.get('name', 'Unknown')

            artists_data = t_info.get('artists', [])
            if artists_data:
                primary_artist_id = artists_data[0]['id']

                artist, created = Artist.objects.get_or_create(
                    id=primary_artist_id,
                    defaults={'name': artists_data[0].get('name', 'Unknown')}
                )

                if created:
                    artist_url = f"https://api.spotify.com/v1/artists/{primary_artist_id}"
                    a_response = requests.get(artist_url, headers=headers)
                    if a_response.status_code == 200:
                        a_info = a_response.json()
                        for genre_name in a_info.get('genres', []):
                            genre, _ = Genre.objects.get_or_create(name=genre_name)
                            artist.genres.add(genre)

                track_db.artist = artist
            track_db.save()
            time.sleep(0.8)

        except Exception as e:
            print(f"Ошибка сети на треке {track_db.id}: {e}")
            time.sleep(2)


if __name__ == '__main__':

    enrich_tracks(5000000)