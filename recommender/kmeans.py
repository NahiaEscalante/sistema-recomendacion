from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import cdist
import numpy as np

class KMeansRecommender:
    def __init__(self, n_clusters=8, random_state=42):
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10, max_iter=300)
        self.scaler = StandardScaler()
        self.X_train = None
        self.movie_ids = None
        self.clusters = None
        self.centroids = None
        self.X_train_scaled = None

    def fit(self, X, movie_ids):
        self.X_train = np.array(X)
        self.movie_ids = np.array(movie_ids)
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.clusters = self.kmeans.fit_predict(self.X_train_scaled)
        self.centroids = self.kmeans.cluster_centers_

    def assign_cluster(self, x):
        x_scaled = self.scaler.transform([x])
        distances = cdist(x_scaled, self.centroids)
        return np.argmin(distances)

    def get_neighbors(self, x, k=10):
        cluster = self.assign_cluster(x)
        mask = self.clusters == cluster
        candidatos = self.X_train_scaled[mask]
        dists = np.linalg.norm(candidatos - self.scaler.transform([x]), axis=1)
        nearest = np.argsort(dists)[:k]
        return self.movie_ids[mask][nearest]
