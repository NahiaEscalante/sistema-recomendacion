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

# Configuración
POSTERS_FOLDER = "data/posters_test/"
MOVIES_CSV = "data/ml-25/movies_test.csv"

@st.cache_data
def load_movies():
    df_movies = pd.read_csv(MOVIES_CSV)
    df_movies = df_movies[['movieId', 'title']].rename(columns={"movieId": "query_movie_id", "title": "query_title"})
    return df_movies

df_movies = load_movies()

# Catálogo de películas
st.markdown("### 🎞️ Catálogo completo de películas:")
catalogo_movies = df_movies.drop_duplicates(subset="query_movie_id")
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
