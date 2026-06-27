import os
import django
import pandas as pd
from tqdm import tqdm  # Библиотека для красивого прогресс-бара (pip install tqdm)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotify_analytics.settings')
django.setup()

from analytics.models import SpotifyUser, Track, Listen


def load_user_data():
    users_df = pd.read_csv('final_users_dataset.csv', sep=';')

    user_objects = []
    for _, row in users_df.iterrows():
        user_objects.append(
            SpotifyUser(
                user_id=row['user_id'],
                age=row['age'],
                gender=row['gender'],
                subscription_plan=row['subscription_plan']
            )
        )
    SpotifyUser.objects.bulk_create(user_objects, batch_size=1000)

    history_df = pd.read_csv('final_listening_history.csv', sep=';')

    unique_tracks = history_df['track_id'].dropna().unique()
    track_objects = [Track(id=t_id) for t_id in unique_tracks]
    Track.objects.bulk_create(track_objects, batch_size=5000)


def load_listening_history():
    history_df = pd.read_csv('final_listening_history.csv', sep=';')
    history_df = history_df.dropna(subset=['track_id', 'listened_at'])
    listen_objects = []
    batch_size = 10000
    for _, row in tqdm(history_df.iterrows(), total=len(history_df)):
        listen_objects.append(
            Listen(
                user_id=row['user_id'],
                track_id=row['track_id'],
                listened_at=row['listened_at']
            )
        )
        if len(listen_objects) == batch_size:
            Listen.objects.bulk_create(listen_objects)
            listen_objects = []
    if listen_objects:
        Listen.objects.bulk_create(listen_objects)


if __name__ == '__main__':
    load_user_data()
    load_listening_history()
