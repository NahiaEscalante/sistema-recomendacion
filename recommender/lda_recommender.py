import pandas as pd
from recommender.kmeans import KMeansRecommender

def recomendar_por_lda(movie_id, top_n=5):
    df = pd.read_csv("data/reduccion_train/features_lda_18.csv")
    lda_cols = [col for col in df.columns if col.startswith("lda_comp_")]
    features = df[lda_cols].values
    movie_ids = df["movieId"].values

    if movie_id not in movie_ids:
        raise ValueError(f"El movie_id {movie_id} no se encuentra en el dataset LDA.")

    idx = df[df["movieId"] == movie_id].index[0]
    vector = features[idx].flatten()

    modelo = KMeansRecommender(n_clusters=10)
    modelo.fit(features, movie_ids)

    recomendaciones = modelo.get_neighbors(vector, k=top_n)

    return list(map(int, recomendaciones))  
