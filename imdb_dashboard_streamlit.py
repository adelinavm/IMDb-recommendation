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

st.title("🎬 IMDb Movie Recommendation")

# --- Rekomendasi Berdasarkan Histori Pencarian Judul ---
st.header("🔎 Rekomendasi Berdasarkan Histori Pencarian Judul")
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

search_title = st.text_input("Cari Judul Film")
if search_title:
    st.session_state['search_history'].append(search_title)
    filtered = df[df['title'].str.lower().str.contains(search_title.lower())]
    st.write(f"Hasil pencarian untuk: {search_title}")
    st.dataframe(filtered[['title', 'year', 'genres', 'rating', 'numVotes']], use_container_width=True)
    # Rekomendasi berdasarkan judul yang mirip
    if not filtered.empty:
        genre_pref = filtered.iloc[0]['genres'].split(', ')[0]
        st.write(f"Rekomendasi film lain dengan genre serupa ({genre_pref}):")
        genre_recs = df[df['genres'].str.contains(genre_pref)].sort_values(by='rating', ascending=False)
        st.table(genre_recs[['title', 'year', 'genres', 'rating']].head(5))

if st.session_state['search_history']:
    st.markdown("**Histori Pencarian Judul:**")
    st.write(st.session_state['search_history'])

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
