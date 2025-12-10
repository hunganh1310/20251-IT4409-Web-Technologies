import os
import json
import time
import logging
import pandas as pd
from typing import Tuple, List, Dict
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from upload_pg import upload_to_postgres
from logging.handlers import RotatingFileHandler

# 1. Config paths
AIRFLOW_HOME = "/opt/airflow"
DATA_DIR = os.path.join(AIRFLOW_HOME, "data")
LOG_DIR = os.path.join(AIRFLOW_HOME, "logs")
PROGRESS_FILE = os.path.join(AIRFLOW_HOME, "progress.json")
DATASET_PATH = os.path.join(DATA_DIR, "dataset.csv")
TRACKS_FILE = os.path.join(AIRFLOW_HOME, "tracks.json")

# 2. Load environment variables
load_dotenv(os.path.join(AIRFLOW_HOME, ".env"))

# 3. Set up logging
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "data_enrich.log")

logger = logging.getLogger("data_enrich")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 4. Spotify client
def sp_client() -> Spotify:
    return Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    ))

    return sp

# 5. Load last batch number
def load_batch_number() -> int:
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f).get("batch_number", 0)
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"batch_number": 0}, f)
    return 0

# 6. Read CSV for current batch
def read_csv(batch_number: int) -> pd.DataFrame:
    if not os.path.exists(DATASET_PATH):
        logger.error(f"Dataset not found at {DATASET_PATH}")
        exit(1)
    
    df = pd.read_csv(DATASET_PATH)
    batch_size = 500  # Reduced from 4000 to avoid Spotify rate limits
    start = batch_number * batch_size
    end = min(start + batch_size, len(df))
    df_batch = df.iloc[start:end]
    
    if df_batch.empty:
        logger.info(f"[Batch {batch_number}] No more tracks to process.")
        exit(0)
    
    return df_batch

# 7. Process batch
def process_batch(df_batch: pd.DataFrame, sp: Spotify, batch_number: int) -> Tuple[Dict, Dict, List, List]:
    albums, artists, songs, album_artists = {}, {}, [], []
    artist_ids = set()
    
    track_ids = df_batch["track_id"].tolist()
    track_batches = [track_ids[i:i+50] for i in range(0, len(track_ids), 50)]
    all_tracks = []

    for batch in track_batches:
        attempt = 1
        backoff = 2
        while attempt <= 5:
            try:
                all_tracks += sp.tracks(batch)["tracks"]
                break
            except Exception as e:
                logger.error(f"[Batch {batch_number}] Track batch fetch error: {e} (Attempt {attempt})")
                time.sleep(backoff)
                attempt += 1
                backoff *= 2

        time.sleep(1)

    for index, track in enumerate(all_tracks):
        logger.info(f"Fetching track's information ({index + 1}/{len(all_tracks)})")

        if not track: continue
        track_id = track["id"]
        row = df_batch[df_batch["track_id"] == track_id].iloc[0]
        album = track["album"]
        album_id = album["id"]

        # Fetch album detail
        if album_id not in albums:
            attempt = 1
            backoff = 2
            while attempt <= 5:
                try:
                    album_data = sp.album(album_id)
                    albums[album_id] = {
                        "id": album_id,
                        "name": album_data["name"],
                        "release_date": album_data["release_date"],
                        "image_url": album_data["images"][0]["url"] if album_data["images"] else None,
                        "type": album_data["album_type"]
                    }
                    for artist in album_data["artists"]:
                        album_artists.append({"album_id": album_id, "artist_id": artist["id"]})
                        artist_ids.add(artist["id"])

                    break
                except Exception as e:
                    logger.error(f"[Batch {batch_number}] Album fetch failed for {album_id}: {e} (Attempt {attempt})")
                    time.sleep(backoff)
                    backoff *= 2
                    attempt += 1

        for artist in track["artists"]:
            artist_ids.add(artist["id"])
            song_data = row[[
                "track_id", "track_name", "popularity", "duration_ms", "explicit", "danceability",
                "energy", "key", "loudness", "mode", "speechiness", "acousticness",
                "instrumentalness", "liveness", "valence", "tempo", "time_signature", "track_genre"
            ]].to_dict()
            song_data.update({
                "album_id": album_id,
                "artist_id": artist["id"],
                "track_image_url": album["images"][0]["url"] if album["images"] else None
            })
            songs.append(song_data)

        time.sleep(1)

    # Batch fetch artists
    artist_ids = list(artist_ids)
    for i in range(0, len(artist_ids), 50):
        attempt = 1
        backoff = 2
        while attempt <= 5:
            try:
                for artist in sp.artists(artist_ids[i:i+50])["artists"]:
                    artists[artist["id"]] = {
                        "id": artist["id"],
                        "name": artist["name"],
                        "followers": artist["followers"]["total"],
                        "image_url": artist["images"][0]["url"] if artist["images"] else None
                    }

                break
            except Exception as e:
                logger.error(f"[Batch {batch_number}] Artist batch fetch error: {e} (Attempt {attempt})")
                time.sleep(backoff)
                backoff *= 2
                attempt += 1
        
        time.sleep(1)

    return albums, artists, songs, album_artists

# 8. Upload to PostgreSQL
def upload_df_to_pg(albums: Dict, artists: Dict, songs: List, album_artists: List, batch_number: int):

    albums_df = pd.DataFrame(albums.values())
    artists_df = pd.DataFrame(artists.values())
    songs_df = pd.DataFrame(songs)
    album_artists_df = pd.DataFrame(album_artists)

    songs_df = songs_df.sort_values("popularity", ascending=False)
    songs_df = songs_df.drop_duplicates(subset=["track_id", "artist_id"])

    album_artists_df = album_artists_df.drop_duplicates(subset=["album_id", "artist_id"])

    logger.info(f"[BATCH {batch_number}] Starting upload of data frames")

    upload_to_postgres(albums_df, "albums", ["id"], logger)
    upload_to_postgres(artists_df, "artists", ["id"], logger)
    upload_to_postgres(songs_df, "songs", ["track_id", "artist_id"], logger)
    upload_to_postgres(album_artists_df, "album_artists", ["album_id", "artist_id"], logger)

    logger.info(f"[Batch {batch_number}] Completed {len(songs_df)} songs, {len(artists_df)} artists, {len(albums_df)} albums")

    upload_batch_number(batch_number)
    upload_tracks_file(songs)

# 9. Save next batch number
def upload_batch_number(batch_number: int):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"batch_number": batch_number + 1}, f)

# 10. Upload all tracks name to download mp3 from youtube
def upload_tracks_file(songs: List[Dict]):
    unique_track_names = set()
    for song in songs:
        track_name = song["track_name"]
        if track_name:
            unique_track_names.add(track_name)

    with open(TRACKS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [{"track_name": name} for name in sorted(unique_track_names)],
            f,
            ensure_ascii=False,
            indent=2
        )

# 11. Main entry
if __name__ == "__main__":
    batch_number = load_batch_number()
    logger.info(f"Loaded batch_number: {batch_number}")
    
    df_batch = read_csv(batch_number)
    logger.info(f"Read CSV with {len(df_batch)} rows")
    
    sp = sp_client()
    logger.info("Initialized Spotify client")
    
    albums, artists, songs, album_artists = process_batch(df_batch, sp, batch_number)
    logger.info("Finished processing batch")

    upload_df_to_pg(albums, artists, songs, album_artists, batch_number)
    logger.info("Upload complete")

    logger.info("All done.")

