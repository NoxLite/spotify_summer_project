import os
import django
import time
import requests

import info

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotify_analytics.settings')
django.setup()

from analytics.models import Artist, Genre

CLIENT_ID = info.CLIENT_ID
CLIENT_SECRET = info.CLIENT_SECRET


def get_new_token():
    url = "https://accounts.spotify.com/api/token"
    response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(CLIENT_ID, CLIENT_SECRET))
    return response.json()['access_token']


def fix_genres():
    # Ищем артистов, у которых вообще нет жанров
    artists_without_genres = Artist.objects.filter(genres__isnull=True).distinct()

    token = get_new_token()
    headers = {"Authorization": f"Bearer {token}"}

    for idx, artist in enumerate(artists_without_genres, 1):
        try:
            url = f"https://api.spotify.com/v1/artists/{artist.id}"
            response = requests.get(url, headers=headers)

            if response.status_code == 401:
                token = get_new_token()
                headers["Authorization"] = f"Bearer {token}"
                response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                for genre_name in data.get('genres', []):
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    artist.genres.add(genre)

            print(f"[{idx}/{len(artists_without_genres)}] Обновлен: {artist.name}")
            time.sleep(0.5)

        except Exception as e:
            print(f"Ошибка на {artist.name}: {e}")




if __name__ == '__main__':
    fix_genres()