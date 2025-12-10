from get_liked_track import get_all_user_ids, get_liked_track_ids
from loader import recommender
from recommender import recommend_songs
import pandas as pd 
from google.cloud import bigquery
from datetime import datetime, timezone 


def main():
    client = bigquery.Client()
    table_id = "silicon-stock-452315-h4.music_recommend.recommend"
    table_id1 = "silicon-stock-452315-h4.music_recommend.emotion-recommend"

    user_ids = get_all_user_ids()
    rows_default = []
    rows_emotion = []

    for user_id in user_ids:
        liked_songs = get_liked_track_ids(user_id)
        if len(liked_songs) < 2:
            print(f"User {user_id} không đủ bài hát!")
            continue

        recommended_songs = recommend_songs(liked_songs)

        # Trường hợp trả về dictionary nhiều cảm xúc
        if isinstance(recommended_songs, dict):
            # Gợi ý mặc định
            for track_id in recommended_songs.get("default", []):
                rows_default.append({
                    "user_id": user_id,
                    "track_id": track_id,
                    "recommended_at": datetime.now(timezone.utc).isoformat()
                })

            # Gợi ý theo cảm xúc
            for emotion, track_ids in recommended_songs.items():
                if emotion == "default":
                    continue
                for track_id in track_ids:
                    rows_emotion.append({
                        "user_id": user_id,
                        "track_id": track_id,
                        "emotion": emotion,
                        "recommended_at": datetime.now(timezone.utc).isoformat()
                    })

        else:
            # Trường hợp trả về list đơn giản
            for track_id in recommended_songs:
                rows_default.append({
                    "user_id": user_id,
                    "track_id": track_id,
                    "recommended_at": datetime.now(timezone.utc).isoformat()
                })

    # Ghi lên BigQuery
    if rows_default:
        errors_default = client.insert_rows_json(table_id, rows_default)
        if not errors_default:
            print("Insert bảng recommend thành công!")
        else:
            print("Lỗi bảng recommend:", errors_default)

    if rows_emotion:
        errors_emotion = client.insert_rows_json(table_id1, rows_emotion)
        if not errors_emotion:
            print("Insert bảng emotion-recommend thành công!")
        else:
            print("Lỗi bảng emotion-recommend:", errors_emotion)

if __name__ == "__main__":
    main()
