from sklearn.preprocessing import normalize
import numpy as np
from loader import recommender
import hdbscan
from get_liked_track import get_liked_track_ids, get_all_user_ids
import faiss

def recommend_songs(liked_track_ids, top_n=10):
    liked_indices = []
    for tid in liked_track_ids:
        matches = recommender.data_df[recommender.data_df['track_id'] == tid].index
        if len(matches) > 0:
            liked_indices.append(matches[0])
    
    if len(liked_indices) == 0:
        print("Không có bài hát nào tồn tại trong data_df khớp với liked_track_ids.")
        return {}

    liked_track_features = recommender.track_features[liked_indices]

    clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
    cluster_labels = clusterer.fit_predict(liked_track_features)

    cluster_centers = []
    for label in np.unique(cluster_labels):
        if label == -1:
            continue
        cluster = liked_track_features[cluster_labels == label]
        center = cluster.mean(axis=0)
        cluster_centers.append(center)

    if len(cluster_centers) == 0:
        print("Không có cụm nào được tạo ra, dùng vector trung bình người dùng.")
        cluster_centers = [np.mean(liked_track_features, axis=0)]

    cluster_centers = normalize(np.array(cluster_centers))

    emotion_filters = {
        "default": None,
        "happy": "Happy",
        "chill": "Chill",
        "sad": "Sad",
        "angry": "Angry",
        "lonely": "Lonely",
    }

    recommendations = {}

    for name, emotion in emotion_filters.items():
        if emotion is None:
            mask = np.ones(len(recommender.data_df), dtype=bool)
        else:
            mask = recommender.data_df['emotion'] == emotion

        filtered_features = recommender.track_features[mask]

        if len(filtered_features) == 0:
            print(f"Không có bài hát nào cho cảm xúc: {emotion}")
            recommendations[name] = []
            continue

        d = filtered_features.shape[1]
        faiss_index = faiss.IndexFlatL2(d)
        faiss_index.add(normalize(filtered_features))

        _, indices = faiss_index.search(cluster_centers, 2 * top_n)

        filtered_indices = recommender.data_df[mask].index.to_numpy()
        recommended_indices = filtered_indices[indices.ravel()]

        # Trích xuất track_id và loại trùng
        track_ids = list(dict.fromkeys([
            recommender.data_df.iloc[i]["track_id"] for i in recommended_indices
        ]))[:top_n*2]

        recommendations[name] = track_ids

    return recommendations
# user_ids = get_all_user_ids()
# for user_id in user_ids:
#     liked_track_ids = get_liked_track_ids(user_id)
#     if len(liked_track_ids) > 0:
#         recommended_track_ids = recommend_songs(liked_track_ids)
#         print(f"Recommended songs for user {user_id}: {recommended_track_ids}")
#     else:
#         print(f"No liked tracks found for user {user_id}")
