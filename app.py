import streamlit as st
import pandas as pd
from PIL import Image
import os
import re

# ===================== ESTILOS =====================
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

# ===================== RUTAS =====================
POSTERS_FOLDER = "data/posters_test/"
POSTERS_CLUSTER_FOLDER = "data/posters_new"
MOVIES_CSV = "data/ml-25/movies_test.csv"
MOVIES_FULL = "data/ml-25/movies.csv" 

# ===================== CARGAR CATÁLOGO =====================
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

    def extract_year(title):
        m = re.match(r'^(.*)\s+\((\d{4})\)$', title)
        if m:
            return int(m.group(2))
        return None

    df_combined['year'] = df_combined['query_title'].apply(extract_year)
    return df_combined

df_movies_with_genres = load_movies()

# ===================== FILTROS =====================
if "selected_genre_prev" not in st.session_state:
    st.session_state.selected_genre_prev = "Todos"
if "selected_year_prev" not in st.session_state:
    st.session_state.selected_year_prev = "Todos"
if "page_number" not in st.session_state:
    st.session_state.page_number = 0

# Géneros
all_genres = set()
df_movies_with_genres['genres'].dropna().apply(lambda x: all_genres.update(x.split('|')))
all_genres = sorted(list(all_genres))

# Años
all_years = df_movies_with_genres['year'].dropna().astype(int).sort_values().unique()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### Filtrar por género:")
    selected_genre = st.selectbox("Selecciona un género:", ["Todos"] + all_genres)

with col2:
    st.markdown("### Filtrar por año:")
    selected_year = st.selectbox("Selecciona un año:", ["Todos"] + list(all_years))

if selected_genre != st.session_state.selected_genre_prev or selected_year != st.session_state.selected_year_prev:
    st.session_state.page_number = 0
    st.session_state.selected_genre_prev = selected_genre
    st.session_state.selected_year_prev = selected_year

df_filtered = df_movies_with_genres.copy()
if selected_genre != "Todos":
    df_filtered = df_filtered[df_filtered['genres'].str.contains(selected_genre, na=False)]
if selected_year != "Todos":
    df_filtered = df_filtered[df_filtered['year'] == int(selected_year)]

# ===================== CATÁLOGO COMPLETO =====================
st.markdown("### 🎞️ Catálogo completo de películas:")
catalogo_movies = df_filtered.drop_duplicates(subset="query_movie_id")

MOVIES_PER_PAGE = 20
total_movies = len(catalogo_movies)
start_idx = st.session_state.page_number * MOVIES_PER_PAGE
end_idx = start_idx + MOVIES_PER_PAGE
catalogo_segment = catalogo_movies.iloc[start_idx:end_idx]

# Navegación
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

# Mostrar películas
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

            if st.button("Ver recomendaciones", key=f"btn_catalog_{movie_id}"):
                st.markdown(f'<meta http-equiv="refresh" content="0; url=/pelicula?movie_id={movie_id}">', unsafe_allow_html=True)



# ===================== b) REPRESENTANTES POR CLUSTER =====================
st.markdown("## 📂 Películas representativas por cluster")

@st.cache_data
def load_top10_cluster():
    df_top10 = pd.read_csv("data/top10_por_cluster.csv", dtype={"movieId": int, "n_cluster": int})
    df_titles = pd.read_csv("data/ml-25/movies_train.csv", dtype={"movieId": int})

    df_top10 = df_top10.rename(columns={"movieId": "query_movie_id"})
    df_titles = df_titles.rename(columns={"movieId": "query_movie_id", "title": "query_title"})

    df_merged = pd.merge(df_top10, df_titles, on="query_movie_id", how="left")
    return df_merged

df_top10 = load_top10_cluster()

# Obtener nombre representativo del cluster (género más común)
def get_main_genre(genre_series):
    all_genres = genre_series.dropna().str.split('|').explode()
    if not all_genres.empty:
        return all_genres.value_counts().idxmax()
    return "Desconocido"

cluster_names = (
    df_top10.groupby('n_cluster')['genre']
    .apply(get_main_genre)
    .reset_index()
    .rename(columns={'genre': 'main_genre'})
)

# Crear diccionario 
cluster_names['cluster_label'] = cluster_names['n_cluster'].astype(str) + " - " + cluster_names['main_genre']
cluster_dict = dict(zip(cluster_names['cluster_label'], cluster_names['n_cluster']))

# Selector
st.markdown("### 🔍 Ver películas representativas por cluster:")
selected_label = st.selectbox("Selecciona un cluster:", list(cluster_dict.keys()))
selected_cluster = cluster_dict[selected_label]

# Mostrar pelis del cluster
cluster_movies = df_top10[df_top10["n_cluster"] == selected_cluster].dropna(subset=["query_movie_id", "query_title"]).reset_index(drop=True)

if cluster_movies.empty:
    st.warning(" No se encontraron películas para este cluster.")
else:
    st.markdown(f"### 🎬 Top 10 del Cluster {selected_label}")
    cols = st.columns(5)
    for idx, row in cluster_movies.iterrows():
        movie_id = int(row["query_movie_id"])
        title = row["query_title"]
        poster_path = os.path.join(POSTERS_CLUSTER_FOLDER, f"{movie_id}.jpg")

        with cols[idx % 5]:
            if os.path.exists(poster_path):
                st.image(Image.open(poster_path), caption=title, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/150x220.png?text=No+Poster", caption=title or f"ID {movie_id}", use_container_width=True)

## UMAP
import umap
import matplotlib.pyplot as plt


# config
st.subheader("Visualización de clusters jerárquicos con UMAP")
st.caption("Clustering en espacio LDA, visualización en 2D")

df = pd.read_csv("data/train_with_clusters.csv")
lda_columns = [col for col in df.columns if col.startswith("lda_comp_")]
X = df[lda_columns]

# umap
umap_model = umap.UMAP(n_components=2, random_state=42)
X_umap = umap_model.fit_transform(X)

df_umap = pd.DataFrame({
    "UMAP_1": X_umap[:, 0],
    "UMAP_2": X_umap[:, 1],
    "Cluster": df["cluster"],
    "Género": df["primary_genre"]
})

centroides = df_umap.groupby("Cluster")[["UMAP_1", "UMAP_2"]].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 10))

for cluster_id in sorted(df_umap["Cluster"].unique()):
    sub_df = df_umap[df_umap["Cluster"] == cluster_id]
    genre_name = sub_df["Género"].mode()[0] if not sub_df["Género"].isnull().all() else "Sin género"
    count = len(sub_df)
    label = f"Cluster {cluster_id} ({genre_name}, n={count})"
    ax.scatter(sub_df["UMAP_1"], sub_df["UMAP_2"], label=label, alpha=0.5, s=25)

# agregar centroides
ax.scatter(centroides["UMAP_1"], centroides["UMAP_2"],
           color="black", marker="X", s=100, label="Centroides")

# etiquetas en centroides
for _, row in centroides.iterrows():
    cluster_id = int(row["Cluster"])
    genre = df_umap[df_umap["Cluster"] == cluster_id]["Género"].mode()[0]
    ax.text(row["UMAP_1"] + 0.5, row["UMAP_2"] + 0.5,
            f"{cluster_id} - {genre}", fontsize=10, color='black', weight='bold')


ax.set_xlim([-15, 25])
ax.set_ylim([-20, 20])
ax.set_title("Visualización de Clusters con UMAP (2D)", fontsize=16, weight='bold')
ax.set_xlabel("UMAP Componente 1")
ax.set_ylabel("UMAP Componente 2")
ax.grid(True, alpha=0.2)
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')

st.pyplot(fig)
