import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("film_detail_complete_fixed.csv")
    df = df.dropna(subset=['title', 'genres', 'rating'])
    df = df[df['title'] != "N/A"]
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])
    df['rating'] = df['rating'].astype(float)
    return df

df = load_data()

# --- Rekomendasi Otomatis Berdasarkan Histori atau Rating Tertinggi ---
st.header("🎬 Rekomendasi Otomatis untuk Kamu")
if 'search_history' in st.session_state and st.session_state['search_history']:
    # Ambil genre dari histori terakhir
    last_title = st.session_state['search_history'][-1]
    filtered = df[df['title'].str.lower().str.contains(last_title.lower())]
    if not filtered.empty:
        genre_pref = filtered.iloc[0]['genres'].split(', ')[0]
        st.write(f"Karena kamu suka film {last_title}, berikut rekomendasi genre {genre_pref}:")
        genre_recs = df[df['genres'].str.contains(genre_pref)].sort_values(by='rating', ascending=False)
        st.table(genre_recs[['title', 'year', 'genres', 'rating']].head(10))
    else:
        st.info("Belum ada data genre dari histori, menampilkan rekomendasi rating tertinggi.")
        st.table(df.sort_values(by='rating', ascending=False)[['title', 'year', 'genres', 'rating']].head(10))
else:
    st.info("Belum ada histori, berikut rekomendasi film rating tertinggi:")
    st.table(df.sort_values(by='rating', ascending=False)[['title', 'year', 'genres', 'rating']].head(10))

# --- Rekomendasi Berdasarkan Mood & Genre ---
st.header("😊 Rekomendasi Berdasarkan Mood & Genre")
mood_map = {
    "Bersemangat": ["Adventure", "Action"],
    "Jatuh Cinta": ["Romance", "Drama"],
    "Berani": ["Thriller", "Crime", "Mystery"],
    "Sedih": ["Drama", "Romance"],
    "Happy": ["Comedy", "Family", "Animation"],
    "Badmood": ["Comedy", "Adventure", "Fantasy"]
}

mood = st.selectbox("Pilih Mood Kamu", list(mood_map.keys()))
user_genre = st.text_input("(Opsional) Tambah Genre Favoritmu", "").strip().title()
target_genres = mood_map[mood].copy()
if user_genre:
    target_genres.append(user_genre)

exploded = df.copy()
exploded['genres'] = exploded['genres'].str.split(", ")
exploded = exploded.explode('genres')

recommend = exploded[exploded['genres'].isin(target_genres)]
recommend = recommend.sort_values(by="rating", ascending=False).drop_duplicates("title")

st.markdown(f"Top rekomendasi untuk mood **{mood}**{f' & genre **{user_genre}**' if user_genre else ''}:")
if not recommend.empty:
    recommend['year'] = recommend['year'].astype(int)
    st.table(recommend[['title', 'year', 'genres', 'rating']].head(10))
else:
    st.info("Tidak ada rekomendasi untuk mood/genre tersebut.")
