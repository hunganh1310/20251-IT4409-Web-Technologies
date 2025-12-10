## IMPORT PACKAGES
import os
import logging
import json
import time
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from minio import Minio
from logging.handlers import RotatingFileHandler

## DEFINE VARIABLE

# Airflow-style paths
AIRFLOW_DIR = "/opt/airflow"
DATA_DIR = os.path.join(AIRFLOW_DIR, "data")
LOGS_DIR = os.path.join(AIRFLOW_DIR, "logs")
ENV_PATH = os.path.join(AIRFLOW_DIR, ".env")
TRACKS_PATH = os.path.join(AIRFLOW_DIR, "tracks.json")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Define logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
file_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, "upload_mp3.log"), maxBytes=5_000_000, backupCount=3
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Load .env file
load_dotenv(ENV_PATH)

# S3 credentials
s3_access_key = os.getenv("S3_ACCESS_KEY")
s3_secret_key = os.getenv("S3_SECRET_KEY")
s3_endpoint = os.getenv("S3_ENDPOINT")
s3_bucket = os.getenv("S3_BUCKET")
s3_prefix = os.getenv("S3_PREFIX", "").strip("/")

## DEFINE FUNCTIONS

# 1. Get all the tracks' name
def get_track_list() -> list[str]:
    with open(TRACKS_PATH, "r", encoding="utf-8") as f:
        tracks_data = json.load(f)
        return [track["track_name"] for track in tracks_data]

# 2. Create S3 client
def s3_client() -> Minio:
    return Minio(
        endpoint=s3_endpoint,
        access_key=s3_access_key,
        secret_key=s3_secret_key,
        secure=False  # Use False for local MinIO without SSL
    )

# 3. Upload file to S3
def upload_to_s3(file_path: str):
    s3 = s3_client()
    file_name = os.path.basename(file_path).lower()
    object_name = f"{s3_prefix}/{file_name}" if s3_prefix else file_name

    s3.fput_object(
        bucket_name=s3_bucket,
        object_name=object_name,
        file_path=file_path,
        content_type="audio/mpeg"
    )
    logger.info(f"Uploaded '{file_name}' to s3://{s3_bucket}/{object_name}")

# 4. Download MP3 from YouTube
def download_mp3(track_name: str) -> str:
    file_name = f"{track_name}.mp3"
    file_path = os.path.join(DATA_DIR, file_name)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path.replace(".mp3", ".%(ext)s"),
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch1:{track_name}"])

    logger.info(f"Downloaded '{track_name}' to '{file_path}'")
    return file_path

## MAIN

if __name__ == "__main__":
    tracks = get_track_list()

    for index, track in enumerate(tracks):
        logger.info(f"Starting process for: {track} ({index + 1}/{len(tracks)})")
        attempt = 1
        backoff = 0.5

        while attempt <= 5:
            try:
                file_path = download_mp3(track)
                upload_to_s3(file_path)
                os.remove(file_path)
                logger.info("Local file cleaned up.")
                break
            except Exception as e:
                logger.error(f"Error during '{track}': {e} (Attempt {attempt})")
                time.sleep(backoff)
                attempt += 1
                backoff *= 2

        time.sleep(0.5)