import streamlit as st
import pandas as pd
from PIL import Image
import os
import re

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

# Rutas
POSTERS_FOLDER = "data/posters_test/"
MOVIES_CSV = "data/ml-25/movies_test.csv"
MOVIES_FULL = "data/ml-25/movies.csv" 

# Cargar y combinar datos
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

    # Extraer el anioo del titulo
    def extract_year(title):
        m = re.match(r'^(.*)\s+\((\d{4})\)$', title)
        if m:
            return int(m.group(2))
        return None

    df_combined['year'] = df_combined['query_title'].apply(extract_year)

    return df_combined

df_movies_with_genres = load_movies()

# Filtros con reinicio de pagina

# Estado inicial
if "selected_genre_prev" not in st.session_state:
    st.session_state.selected_genre_prev = "Todos"
if "selected_year_prev" not in st.session_state:
    st.session_state.selected_year_prev = "Todos"
if "page_number" not in st.session_state:
    st.session_state.page_number = 0

# Filtro por genero
all_genres = set()
df_movies_with_genres['genres'].dropna().apply(lambda x: all_genres.update(x.split('|')))
all_genres = sorted(list(all_genres))

# Filtro por anio
all_years = df_movies_with_genres['year'].dropna().astype(int).sort_values().unique()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### Filtrar por género:")
    selected_genre = st.selectbox("Selecciona un género:", ["Todos"] + all_genres)

with col2:
    st.markdown("### Filtrar por año:")
    selected_year = st.selectbox("Selecciona un año:", ["Todos"] + list(all_years))

# Si cambian los filtros, reinicia pagina
if selected_genre != st.session_state.selected_genre_prev or selected_year != st.session_state.selected_year_prev:
    st.session_state.page_number = 0
    st.session_state.selected_genre_prev = selected_genre
    st.session_state.selected_year_prev = selected_year

# filtros aplicados 
df_filtered = df_movies_with_genres.copy()

if selected_genre != "Todos":
    df_filtered = df_filtered[df_filtered['genres'].str.contains(selected_genre, na=False)]

if selected_year != "Todos":
    df_filtered = df_filtered[df_filtered['year'] == int(selected_year)]


st.markdown("### 🎞️ Catálogo completo de películas:")
catalogo_movies = df_filtered.drop_duplicates(subset="query_movie_id")

#paginacion
MOVIES_PER_PAGE = 20
total_movies = len(catalogo_movies)
start_idx = st.session_state.page_number * MOVIES_PER_PAGE
end_idx = start_idx + MOVIES_PER_PAGE
catalogo_segment = catalogo_movies.iloc[start_idx:end_idx]

# Navegacion
col_left, col_center, col_right = st.columns([1, 3, 1])
with col_left:
    if st.session_state.page_number > 0:
        if st.button("⬅️ Anterior"):
            st.session_state.page_number -= 1
with col_right:
    if end_idx < total_movies:
        if st.button("Siguiente ➡️"):
            st.session_state.page_number += 1

st.markdown(f"<p style='text-align:center; color:white;'>Página {st.session_state.page_number + 1} de {((total_movies - 1) // MOVIES_PER_PAGE) + 1}</p>", unsafe_allow_html=True)

# Mostrar pelis
for i in range(0, len(catalogo_segment), 5):
    row_data = catalogo_segment.iloc[i:i+5]
    cols = st.columns(5)
    for col, (_, row) in zip(cols, row_data.iterrows()):
        movie_id = row["query_movie_id"]
        title = row["query_title"]
        poster_path = os.path.join(POSTERS_FOLDER, f"{movie_id}.jpg")

        with col:
            if os.path.exists(poster_path):
                st.image(Image.open(poster_path), caption=title, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/150x220.png?text=No+Poster", caption=title, use_container_width=True)

            if st.button("Ver recomendaciones", key=f"btn_{movie_id}"):
                st.markdown(f'<meta http-equiv="refresh" content="0; url=/pelicula?movie_id={movie_id}">', unsafe_allow_html=True)

