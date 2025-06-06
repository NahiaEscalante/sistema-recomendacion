import streamlit as st
import pandas as pd
import os
from PIL import Image

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("/data/ml-25/movies_train.csv")
    return df

df = load_data()

# Obtener lista única de películas query para autocompletar
peliculas_query = df[['query_movie_id', 'title_test']].drop_duplicates().reset_index(drop=True)

# Buscador interactivo con autocompletado (usamos st.selectbox)
st.title("🎬 Bienvenido al Recomendador de Películas con Machine Learning")

st.write("Busca y selecciona una película para ver recomendaciones:")

# Lista de títulos para seleccionar (puedes filtrar más abajo con texto si quieres)
pelicula_seleccionada = st.selectbox(
    "Selecciona la película",
    peliculas_query['title_test'].tolist()
)

# Mostrar info básica de la película seleccionada
if pelicula_seleccionada:
    info_pelicula = peliculas_query[peliculas_query['title_test'] == pelicula_seleccionada].iloc[0]
    st.markdown(f"*Título:* {info_pelicula['title_test']}")
    st.markdown(f"*Movie ID:* {info_pelicula['query_movie_id']}")


# Carpeta donde están los posters
POSTERS_TEST_DIR = "posters_test"
POSTERS_TRAIN_DIR = "posters"

def mostrar_poster(movie_id, carpeta, width=150):
    ruta_poster = os.path.join(carpeta, f"{movie_id}.jpg")
    if os.path.exists(ruta_poster):
        img = Image.open(ruta_poster)
        st.image(img, width=width)
    else:
        st.write("Poster no disponible")

# Tras seleccionar la película:
if pelicula_seleccionada:
    info_pelicula = peliculas_query[peliculas_query['title_test'] == pelicula_seleccionada].iloc[0]
    query_id = info_pelicula['query_movie_id']

    st.markdown("### 🎥 Película seleccionada")
    st.write(f"*Título:* {pelicula_seleccionada}")
    st.write(f"*ID:* {query_id}")
    mostrar_poster(query_id, POSTERS_TEST_DIR, width=200)

    # Filtrar recomendaciones ordenadas por posición para esta película
    recomendaciones = df[(df['query_movie_id'] == query_id)].sort_values('position')

    st.markdown("### 🍿 Recomendaciones")

    # Mostrar en columnas los posters y títulos de las recomendadas
    cols = st.columns(5)
    for idx, (_, row) in enumerate(recomendaciones.iterrows()):
        col = cols[idx % 5]
        with col:
            mostrar_poster(row['recommended_movie_id'], POSTERS_TRAIN_DIR, width=120)
            col.write(f"{row['title_train']}")
            col.write(f"{row['genre_train']} | {int(row['year_train']) if not pd.isna(row['year_train']) else 'N/A'}")
            col.write(f"Pos: {row['position']}")