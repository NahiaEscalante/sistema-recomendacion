import streamlit as st
import pandas as pd
from PIL import Image
import os

# Estilo Netflix
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #141414;
        color: white;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .title-netflix {
        font-size: 3.5em;
        font-weight: bold;
        color: #e50914;
        text-shadow: 2px 2px 8px #000000;
        text-align: center;
        margin-bottom: 30px;
    }
    img {
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .stButton>button {
        background-color: #e50914;
        color: white;
        border-radius: 5px;
        padding: 0.5em 1.5em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #f40612;
    }
    </style>
    <div class="title-netflix">Nefli</div>
""", unsafe_allow_html=True)

POSTERS_FOLDER = "data/posters_test/"
POSTERS_FOLDER_SEC = "data/posters_new/"
MOVIES_CSV = "data/ml-25/movies_test.csv"
MOVIES_CSV_SEC = "data/ml-25/movies_train.csv"
RECO_CSV = "data/submission_files/submission_kmeans_lda_k12.csv"

@st.cache_data
def load_data():
    df_reco = pd.read_csv(RECO_CSV)
    df_movies = pd.read_csv(MOVIES_CSV)[['movieId', 'title']].rename(columns={"movieId": "query_movie_id", "title": "query_title"})
    df_movies_sec = pd.read_csv(MOVIES_CSV_SEC)[['movieId', 'title']].rename(columns={"movieId": "query_movie_id", "title": "query_title"})
    return df_reco, df_movies, df_movies_sec

df_reco, df_movies, df_movies_sec = load_data()

# Obtener movie_id desde parámetros
movie_id = int(st.query_params.get("movie_id", 0))

# 🔒 Aseguramos tipos
df_movies["query_movie_id"] = df_movies["query_movie_id"].astype(int)

# 🔐 Validación
if movie_id not in df_movies["query_movie_id"].values:
    st.error("No se encontró la película seleccionada.")
    st.stop()

# ✅ Obtener título
selected_title = df_movies[df_movies["query_movie_id"] == movie_id]["query_title"].values[0]
st.subheader(f"Película seleccionada: {selected_title}")

poster_path = os.path.join(POSTERS_FOLDER, f"{movie_id}.jpg")
if os.path.exists(poster_path):
    st.image(Image.open(poster_path), caption=selected_title, use_container_width=True)
else:
    st.warning("Poster no disponible.")

# Mostrar recomendaciones
st.markdown("### 🎯 Películas recomendadas:")
recommended_ids = df_reco[df_reco["query_movie_id"] == movie_id]["recommended_movie_id"].tolist()
recommended_movies = df_movies_sec[df_movies_sec["query_movie_id"].isin(recommended_ids)]

cols = st.columns(5)
for idx, rec_id in enumerate(recommended_ids[:10]):
    rec_title = recommended_movies[recommended_movies["query_movie_id"] == rec_id]["query_title"].values
    rec_title = rec_title[0] if len(rec_title) > 0 else f"ID: {rec_id}"
    rec_poster = os.path.join(POSTERS_FOLDER_SEC, f"{rec_id}.jpg")
    with cols[idx % 5]:
        if os.path.exists(rec_poster):
            st.image(Image.open(rec_poster), caption=rec_title, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/150x220.png?text=No+Poster", caption=rec_title, use_container_width=True)

# Botón para regresar
if st.button("⬅️ Volver al catálogo"):
    st.markdown('<meta http-equiv="refresh" content="0; url=/">', unsafe_allow_html=True)


