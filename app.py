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

# Configuración de rutas
POSTERS_FOLDER = "data/posters_test/"
MOVIES_CSV = "data/ml-25/movies_test.csv"
MOVIES_FULL = "data/ml-25/movies.csv"  # Este archivo contiene los géneros reales

# 🔄 Cargar y combinar datos
@st.cache_data
def load_movies():
    df_test = pd.read_csv(MOVIES_CSV)
    df_test = df_test[['movieId', 'title']].rename(columns={
        "movieId": "query_movie_id",
        "title": "query_title"
    })

    df_full = pd.read_csv(MOVIES_FULL)
    df_full = df_full.rename(columns={
        "movieId": "query_movie_id",
        "title": "query_title"
    })

    df_combined = pd.merge(df_test, df_full[['query_movie_id', 'genres']], on="query_movie_id", how="left")
    return pd.merge(df_test, df_combined[['query_movie_id', 'genres']], on="query_movie_id", how="left")

df_movies_with_genres = load_movies()

# 🎯 Filtro visual
all_genres = set()
df_movies_with_genres['genres'].dropna().apply(lambda x: all_genres.update(x.split('|')))
all_genres = sorted(list(all_genres))

st.markdown("### 🎯 Filtrar por género:")
selected_genre = st.selectbox("Selecciona un género:", ["Todos"] + all_genres)

# 📌 Aplicar filtro si se selecciona un género
if selected_genre != "Todos":
    df_filtered = df_movies_with_genres[df_movies_with_genres['genres'].str.contains(selected_genre, na=False)]
else:
    df_filtered = df_movies_with_genres

# 🎞️ Catálogo de películas
st.markdown("### 🎞️ Catálogo completo de películas:")
catalogo_movies = df_filtered.drop_duplicates(subset="query_movie_id")
cols = st.columns(5)

for idx, row in catalogo_movies.iterrows():
    movie_id = row["query_movie_id"]
    title = row["query_title"]
    poster_path = os.path.join(POSTERS_FOLDER, f"{movie_id}.jpg")

    with cols[idx % 5]:
        if os.path.exists(poster_path):
            st.image(Image.open(poster_path), caption=title, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/150x220.png?text=No+Poster", caption=title, use_container_width=True)

        if st.button("Ver recomendaciones", key=f"btn_{movie_id}"):
            st.markdown(f'<meta http-equiv="refresh" content="0; url=/pelicula?movie_id={movie_id}">', unsafe_allow_html=True)
