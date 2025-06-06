import pandas as pd
from recommender.kmeans import KMeansRecommender

def recomendar_por_svd(movie_id, top_n=5):
    df = pd.read_csv("data/reduccion_train/features_svd_20.csv")
    features = df.iloc[:, 2:].values
    movie_ids = df["movieId"].values

    if movie_id not in movie_ids:
        raise ValueError(f"El movie_id {movie_id} no se encuentra en el dataset SVD.")

    idx = df[df["movieId"] == movie_id].index[0]
    vector = features[idx]

    modelo = KMeansRecommender()
    modelo.fit(features, movie_ids)

    recomendaciones = modelo.get_neighbors(vector, k=top_n)
    return list(map(int, recomendaciones))
