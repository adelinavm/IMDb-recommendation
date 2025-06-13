import os
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

def show_header():
    st.title("🎬 IMDb Movie Dashboard - 1 Adik 4 Kakak")

# Load data CSV sekali saja di sini
def load_movie_data():
    csv_path = os.path.join(os.path.dirname(__file__), 'film_detail_complete_fixed.csv')
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['title', 'genres', 'rating'])
    df = df[df['title'] != "N/A"]
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])
    df['rating'] = df['rating'].astype(float)
    return df

def filter_and_display(df):
    st.title("🎬 IMDb Movie Dashboard - 1 Adik 4 Kakak")
    st.subheader("📄 Film Sesuai Filter", anchor=False)
    st.sidebar.header("🔎 Filter Film")
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    year_range = st.sidebar.slider("Tahun Rilis", min_year, 2025, (2000, 2025))
    rating_min = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 7.0, 0.1)
    all_genres = sorted(set(g for sublist in df['genres'].str.split(', ') for g in sublist))
    genre_input = st.sidebar.selectbox("Pilih Genre", ["Semua Genre"] + all_genres)
    title_input = st.sidebar.text_input("Cari Judul Film", "").strip().lower()

    filtered = df[
        (df['year'].between(year_range[0], year_range[1])) &
        (df['rating'] >= rating_min)
    ]
    if genre_input != "Semua Genre":
        filtered = filtered[filtered['genres'].str.contains(genre_input, case=False)]
    if title_input:
        filtered = filtered[filtered['title'].str.lower().str.contains(title_input)]

    # Tampilkan tabel hasil filter rata kiri (default Streamlit)
    if filtered.empty:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    else:
        st.dataframe(filtered[['title', 'year', 'genres', 'rating', 'numVotes']])



