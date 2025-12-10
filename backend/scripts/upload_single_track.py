"""
Script to upload a single missing track to MinIO.
Downloads the audio from YouTube and uploads to S3/MinIO.

Usage:
    cd backend
    python scripts/upload_single_track.py "Track Name Here"
    
Example:
    python scripts/upload_single_track.py "All I Want For Christmas Is A Real Good Tan"
"""
import os
import sys
from dotenv import load_dotenv
from minio import Minio
from yt_dlp import YoutubeDL
import tempfile

# Load environment variables from backend/.env
load_dotenv(override=True)

# S3/MinIO credentials
s3_access_key = os.getenv("S3_ACCESS_KEY")
s3_secret_key = os.getenv("S3_SECRET_KEY")
s3_endpoint = os.getenv("S3_ENDPOINT", "http://localhost:9000")
s3_bucket = os.getenv("S3_BUCKET", "music")
s3_prefix = os.getenv("S3_PREFIX", "tracks").strip("/")


def s3_client() -> Minio:
    """Create MinIO client"""
    endpoint = s3_endpoint
    secure = False
    if endpoint.startswith("https://"):
        endpoint = endpoint[8:]
        secure = True
    elif endpoint.startswith("http://"):
        endpoint = endpoint[7:]
        secure = False
    
    return Minio(
        endpoint=endpoint,
        access_key=s3_access_key,
        secret_key=s3_secret_key,
        secure=secure
    )


def list_existing_tracks():
    """List all existing tracks in MinIO"""
    client = s3_client()
    print(f"\n📁 Existing tracks in s3://{s3_bucket}/{s3_prefix}/:")
    print("-" * 50)
    count = 0
    for obj in client.list_objects(s3_bucket, prefix=s3_prefix, recursive=True):
        print(f"  - {obj.object_name}")
        count += 1
    print(f"\nTotal: {count} tracks")
    return count


def check_track_exists(track_name: str) -> bool:
    """Check if track already exists in MinIO"""
    client = s3_client()
    object_name = f"{s3_prefix}/{track_name.lower()}.mp3"
    try:
        client.stat_object(s3_bucket, object_name)
        return True
    except:
        return False


def download_mp3(track_name: str, output_dir: str) -> str:
    """Download MP3 from YouTube"""
    file_path = os.path.join(output_dir, f"{track_name}.mp3")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path.replace(".mp3", ".%(ext)s"),
        'quiet': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    print(f"🔍 Searching YouTube for: {track_name}")
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch1:{track_name}"])

    print(f"✅ Downloaded to: {file_path}")
    return file_path


def upload_to_s3(file_path: str, track_name: str):
    """Upload file to MinIO"""
    client = s3_client()
    
    # Ensure bucket exists
    if not client.bucket_exists(s3_bucket):
        client.make_bucket(s3_bucket)
        print(f"📦 Created bucket: {s3_bucket}")
    
    object_name = f"{s3_prefix}/{track_name.lower()}.mp3"
    
    client.fput_object(
        bucket_name=s3_bucket,
        object_name=object_name,
        file_path=file_path,
        content_type="audio/mpeg"
    )
    print(f"✅ Uploaded to: s3://{s3_bucket}/{object_name}")


def upload_track(track_name: str):
    """Download and upload a single track"""
    print(f"\n🎵 Processing: {track_name}")
    print("=" * 50)
    
    # Check if already exists
    if check_track_exists(track_name):
        print(f"⚠️  Track already exists in MinIO, skipping...")
        return
    
    # Create temp directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Download from YouTube
            file_path = download_mp3(track_name, temp_dir)
            
            # Upload to MinIO
            upload_to_s3(file_path, track_name)
            
            print(f"\n🎉 Successfully uploaded: {track_name}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_single_track.py <track_name>")
        print("       python upload_single_track.py --list")
        print("\nExample:")
        print('  python upload_single_track.py "All I Want For Christmas Is A Real Good Tan"')
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_existing_tracks()
    else:
        track_name = " ".join(sys.argv[1:])
        upload_track(track_name)


if __name__ == "__main__":
    main()
