import os, pickle, faiss
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize

# Path to local data
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "airflow", "data")
DATASET_PATH = os.path.join(DATA_DIR, "dataset.csv")

# Feature columns for recommendation
FEATURE_COLUMNS = [
    'danceability', 'energy', 'loudness', 'speechiness', 
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
]

class Recommender:
    def __init__(self):
        self.data_df = None
        self.faiss_index = None
        self.track_features = None

    def load(self):
        print("Loading dataset from local file...")
        self.data_df = self.load_data()
        print(f"Loaded {len(self.data_df)} tracks")
        
        print("Generating track features...")
        self.track_features = self.generate_track_features()
        
        print("Building FAISS index...")
        self.faiss_index = self.build_faiss_index()
        print("Done loading recommender.")

    def load_data(self):
        df = pd.read_csv(DATASET_PATH)
        
        # Add emotion column based on audio features if not present
        if 'emotion' not in df.columns:
            df['emotion'] = df.apply(self._classify_emotion, axis=1)
        
        return df

    def _classify_emotion(self, row):
        """Classify song emotion based on audio features"""
        valence = row.get('valence', 0.5)
        energy = row.get('energy', 0.5)
        tempo = row.get('tempo', 120)
        
        if valence > 0.6 and energy > 0.6:
            return 'Happy'
        elif valence < 0.4 and energy < 0.4:
            return 'Sad'
        elif energy > 0.7 and valence < 0.5:
            return 'Angry'
        elif valence < 0.4 and energy < 0.5:
            return 'Lonely'
        else:
            return 'Chill'

    def generate_track_features(self):
        """Generate normalized feature vectors for all tracks"""
        features = self.data_df[FEATURE_COLUMNS].fillna(0).values
        return normalize(features).astype('float32')

    def build_faiss_index(self):
        """Build FAISS index from track features"""
        d = self.track_features.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(self.track_features)
        return index

recommender = Recommender()
print("Loading models...")
recommender.load()
print("Done.")
