"""
Quick upload script - uploads data directly from dataset.csv to PostgreSQL
without using Spotify API. This avoids rate limits.
Also generates tracks.json for MP3 downloading.
"""
import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
AIRFLOW_HOME = "/opt/airflow"
load_dotenv(os.path.join(AIRFLOW_HOME, ".env"))

# PostgreSQL connection
pg_user = os.getenv("POSTGRES_USER")
pg_password = os.getenv("POSTGRES_PASSWORD")
pg_host = os.getenv("POSTGRES_HOST")
pg_port = os.getenv("POSTGRES_PORT")
pg_database = os.getenv("POSTGRES_DATABASE")

engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}")

# Configuration
DATASET_PATH = os.path.join(AIRFLOW_HOME, "data", "dataset.csv")
TRACKS_FILE = os.path.join(AIRFLOW_HOME, "tracks.json")
NUM_ROWS = 500  # Number of rows to upload

def main():
    print(f"Reading {NUM_ROWS} rows from dataset...")
    df = pd.read_csv(DATASET_PATH, nrows=NUM_ROWS)
    
    # Extract unique artists
    artists_set = set()
    for artists_str in df['artists'].dropna():
        for artist in artists_str.split(';'):
            artists_set.add(artist.strip())
    
    artists_df = pd.DataFrame({
        'id': [f"artist_{i}" for i in range(len(artists_set))],
        'name': list(artists_set),
        'image_url': [None] * len(artists_set)
    })
    
    # Create artist name to id mapping
    artist_name_to_id = dict(zip(artists_df['name'], artists_df['id']))
    
    # Extract unique albums
    albums_df = df[['album_name']].drop_duplicates().reset_index(drop=True)
    albums_df['id'] = [f"album_{i}" for i in range(len(albums_df))]
    albums_df['image_url'] = None
    albums_df = albums_df.rename(columns={'album_name': 'name'})
    albums_df = albums_df[['id', 'name', 'image_url']]
    
    # Create album name to id mapping
    album_name_to_id = dict(zip(df['album_name'], [f"album_{i}" for i in range(len(df['album_name'].unique()))]))
    
    # Rebuild album_name_to_id properly
    unique_albums = df['album_name'].unique()
    album_name_to_id = {name: f"album_{i}" for i, name in enumerate(unique_albums)}
    
    # Create songs dataframe - match actual database schema
    songs_data = []
    album_artists_data = []
    
    for _, row in df.iterrows():
        track_id = row['track_id']
        album_name = row['album_name']
        album_id = album_name_to_id.get(album_name, f"album_unknown")
        
        # Get first artist as primary
        artists_str = row['artists'] if pd.notna(row['artists']) else "Unknown"
        artist_list = [a.strip() for a in artists_str.split(';')]
        primary_artist = artist_list[0]
        artist_id = artist_name_to_id.get(primary_artist, "artist_unknown")
        
        songs_data.append({
            'track_id': track_id,
            'track_name': row['track_name'],
            'artist_id': artist_id,
            'album_id': album_id,
            'duration_ms': int(row['duration_ms']) if pd.notna(row['duration_ms']) else 0,
            'popularity': int(row['popularity']) if pd.notna(row['popularity']) else 0,
            'explicit': bool(row['explicit']) if pd.notna(row.get('explicit')) else False,
            'danceability': float(row['danceability']) if pd.notna(row.get('danceability')) else None,
            'energy': float(row['energy']) if pd.notna(row.get('energy')) else None,
            'key': int(row['key']) if pd.notna(row.get('key')) else None,
            'loudness': float(row['loudness']) if pd.notna(row.get('loudness')) else None,
            'mode': int(row['mode']) if pd.notna(row.get('mode')) else None,
            'speechiness': float(row['speechiness']) if pd.notna(row.get('speechiness')) else None,
            'acousticness': float(row['acousticness']) if pd.notna(row.get('acousticness')) else None,
            'instrumentalness': float(row['instrumentalness']) if pd.notna(row.get('instrumentalness')) else None,
            'liveness': float(row['liveness']) if pd.notna(row.get('liveness')) else None,
            'valence': float(row['valence']) if pd.notna(row.get('valence')) else None,
            'tempo': float(row['tempo']) if pd.notna(row.get('tempo')) else None,
            'time_signature': int(row['time_signature']) if pd.notna(row.get('time_signature')) else None,
            'track_genre': row['track_genre'] if pd.notna(row.get('track_genre')) else None,
            'track_image_url': None
        })
        
        # Album artists relationship
        for artist_name in artist_list:
            aid = artist_name_to_id.get(artist_name)
            if aid:
                album_artists_data.append({
                    'album_id': album_id,
                    'artist_id': aid
                })
    
    songs_df = pd.DataFrame(songs_data)
    album_artists_df = pd.DataFrame(album_artists_data).drop_duplicates()
    
    print(f"Prepared data:")
    print(f"  - {len(artists_df)} artists")
    print(f"  - {len(albums_df)} albums")
    print(f"  - {len(songs_df)} songs")
    print(f"  - {len(album_artists_df)} album-artist relationships")
    
    # Upload to PostgreSQL
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Clear existing data (optional)
            print("Clearing existing data...")
            conn.execute(text("DELETE FROM album_artists"))
            conn.execute(text("DELETE FROM songs"))
            conn.execute(text("DELETE FROM albums"))
            conn.execute(text("DELETE FROM artists"))
            
            print("Uploading artists...")
            artists_df.to_sql('artists', conn, if_exists='append', index=False)
            
            print("Uploading albums...")
            albums_df.to_sql('albums', conn, if_exists='append', index=False)
            
            print("Uploading songs...")
            songs_df.to_sql('songs', conn, if_exists='append', index=False)
            
            print("Uploading album_artists...")
            album_artists_df.to_sql('album_artists', conn, if_exists='append', index=False)
            
            trans.commit()
            print("✅ Upload complete!")
            
            # Generate tracks.json for MP3 downloading
            print("Generating tracks.json for MP3 downloads...")
            unique_tracks = df['track_name'].dropna().unique().tolist()
            tracks_data = [{"track_name": name} for name in unique_tracks]
            with open(TRACKS_FILE, "w", encoding="utf-8") as f:
                json.dump(tracks_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Generated tracks.json with {len(tracks_data)} tracks")
            print(f"\nTo download MP3s, run: python /opt/airflow/upload_mp3.py")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error: {e}")
            raise

if __name__ == "__main__":
    main()
