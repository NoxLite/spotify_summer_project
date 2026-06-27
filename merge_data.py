import pandas as pd
import numpy as np

profiles_file = 'data/Spotify_data.csv'
columns_to_keep = ['Age', 'Gender', 'spotify_subscription_plan']

users_df = pd.read_csv(profiles_file, usecols=columns_to_keep, sep=";")
users_df.columns = ['age', 'gender', 'subscription_plan']
users_df.insert(0, 'user_id', [f"user_{i}" for i in range(1, len(users_df) + 1)])

def clean_track_id(uri):
    if pd.isna(uri):
        return np.nan
    return str(uri).replace('spotify:track:', '')

history_frames = []

file1 = 'data/listening_history.csv'

try:
    df1 = pd.read_csv(file1, usecols=['timestamp', 'track_uri'])
    df1.rename(columns={'timestamp': 'listened_at', 'track_uri': 'track_id'}, inplace=True)
    history_frames.append(df1)
    print(f"Успешно загружен {file1}")
except Exception as e:
    print(f"{file1}: {e}")

file2 = 'data/spotify_history-selected-columns.csv'
try:
    df2 = pd.read_csv(file2, usecols=['ts', 'spotify_track_uri'])
    df2.rename(columns={'ts': 'listened_at', 'spotify_track_uri': 'track_id'}, inplace=True)
    history_frames.append(df2)
    print(f"Успешно загружен {file2}")
except Exception as e:
    print(f"{file2}: {e}")

file3 = 'data/spotify_history-selected-columns (2).csv'
try:
    df3 = pd.read_csv(file3, usecols=['ts', 'spotify_track_uri'])
    df3.rename(columns={'ts': 'listened_at', 'spotify_track_uri': 'track_id'}, inplace=True)
    history_frames.append(df3)
    print(f"Успешно загружен {file3}")
except Exception as e:
    print(f"{file3}: {e}")

combined_history = pd.concat(history_frames, ignore_index=True)

combined_history.dropna(subset=['track_id', 'listened_at'], inplace=True)

combined_history['track_id'] = combined_history['track_id'].apply(clean_track_id)

combined_history['listened_at'] = pd.to_datetime(combined_history['listened_at'], format='mixed', utc=True)

random_user_ids = np.random.choice(users_df['user_id'], size=len(combined_history))

combined_history.insert(0, 'user_id', random_user_ids)


# Масштабируем данные
expanded_frames = [combined_history]

for i in range(1, 5):
    history_copy = combined_history.copy()
    history_copy['listened_at'] = history_copy['listened_at'] - pd.Timedelta(days=30 * i)
    expanded_frames.append(history_copy)

combined_history = pd.concat(expanded_frames, ignore_index=True)
output_users_file = 'final_users_dataset.csv'
users_df.to_csv(output_users_file, index=False, sep=";")

output_history_file = 'final_listening_history.csv'
combined_history.to_csv(output_history_file, index=False, sep=";")
