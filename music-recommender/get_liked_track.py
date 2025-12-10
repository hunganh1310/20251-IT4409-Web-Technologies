from base import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text

db = SessionLocal()

def get_all_user_ids():
    query = text("SELECT id FROM users")
    result = db.execute(query).fetchall()
    return [row[0] for row in result]

def get_liked_track_ids(user_id: str):
    query = text("""
        SELECT pt.track_id
        FROM playlist_tracks pt
        INNER JOIN playlist_user pu ON pu.playlist_id = pt.playlist_id
        INNER JOIN playlists p ON p.id = pt.playlist_id
        WHERE pu.user_id = :user_id AND p.name = 'Liked Songs'
        LIMIT 10
    """)
    result = db.execute(query, {"user_id": user_id}).fetchall()
    return [row[0] for row in result]

# ids = get_liked_track_ids("be9062e7-14ff-453d-bae7-fd7a39cf16ab")
# print(ids)
# print(get_all_user_ids())