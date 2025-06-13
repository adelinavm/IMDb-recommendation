import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import os
from auth_utils import authenticate_user, register_user
import sidebar

def load_data():
    df = pd.read_csv("film_detail_complete_fixed.csv")
    df = df.dropna(subset=['title', 'genres', 'rating', 'year'])
    df = df[df['title'] != "N/A"]
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['rating', 'year'])
    df['rating'] = df['rating'].astype(float)
    df['year'] = df['year'].astype(int)
    return df

# --- Auth Section ---
def login_page():
    st.title("🔐 Login IMDb Dashboard")
    login_tab, register_tab = st.tabs(["Login", "Register"])
    with login_tab:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Username/password salah.")
    with register_tab:
        new_user = st.text_input("Username Baru", key="reg_user")
        new_pass = st.text_input("Password Baru", type="password", key="reg_pass")
        if st.button("Register"):
            ok, msg = register_user(new_user, new_pass)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# --- Main Dashboard ---
def main_dashboard():
    sidebar.show_header()
    df = sidebar.load_movie_data()
    sidebar.filter_and_display(df)

    st.header("🎬 Rekomendasi Film")
    rekom_df = load_data()

    # --- Search & Mood Recommendation ---
    if 'search_history' not in st.session_state:
        st.session_state['search_history'] = []

    search_title = st.text_input("Cari Judul Film (Rekomendasi)")
    if search_title:
        st.session_state['search_history'].append(search_title)
        filtered = rekom_df[rekom_df['title'].str.lower().str.contains(search_title.lower())]
        st.write(f"Hasil pencarian untuk: {search_title}")
        st.dataframe(filtered[['title', 'year', 'genres', 'rating', 'numVotes']], use_container_width=True)

        if not filtered.empty:
            genre_pref = filtered.iloc[0]['genres'].split(', ')[0]
            st.write(f"Rekomendasi film lain dengan genre serupa ({genre_pref}):")
            genre_recs = rekom_df[rekom_df['genres'].str.contains(genre_pref)]
            genre_recs = genre_recs.sort_values(by='rating', ascending=False).drop_duplicates('title')
            genre_recs['rating'] = genre_recs['rating'].map(lambda x: f"{x:.1f}")
            st.table(genre_recs[['title', 'year', 'genres', 'rating']].head(5))

    if st.session_state['search_history']:
        st.markdown("**Histori Pencarian Judul:**")
        st.write(st.session_state['search_history'])

    # --- Mood Recommendation ---
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

    exploded = rekom_df.copy()
    exploded['genres'] = exploded['genres'].str.split(", ")
    exploded = exploded.explode('genres')

    recommend = exploded[exploded['genres'].isin(target_genres)]
    recommend = recommend.sort_values(by="rating", ascending=False).drop_duplicates("title")

    recommend['rating'] = recommend['rating'].map(lambda x: f"{x:.1f}")

    st.markdown(f"Top rekomendasi untuk mood **{mood}**{f' & genre **{user_genre}**' if user_genre else ''}:")
    if not recommend.empty:
        st.table(recommend[['title', 'year', 'genres', 'rating']].head(10))
    else:
        st.info("Tidak ada rekomendasi untuk mood/genre tersebut.")

    # --- Trend Visualization ---
    st.header("📈 Tren Film Saat Ini")
    latest_year = int(exploded['year'].max())
    trend_data = exploded[exploded['year'] >= latest_year - 5]
    trend = trend_data.groupby(['year', 'genres']).size().reset_index(name='count')

    import plotly.express as px
    all_genres = sorted(trend['genres'].unique())
    selected_genre = st.selectbox("Pilih Genre (Tren)", ["Semua Genre"] + all_genres)

    if selected_genre != "Semua Genre":
        trend_filtered = trend[trend['genres'] == selected_genre]
    else:
        trend_filtered = trend

    fig2 = px.line(
        trend_filtered,
        x='year',
        y='count',
        color='genres',
        markers=True,
        hover_data=['genres', 'count'],
        labels={'count': 'Jumlah Film', 'year': 'Tahun', 'genres': 'Genre'},
        title='Jumlah Film per Genre (5 Tahun Terakhir)'
    )
    st.plotly_chart(fig2, use_container_width=True)

    if selected_genre != "Semua Genre":
        st.subheader(f"🏆 Top 10 Film Terlaris dalam Genre '{selected_genre}'")
        top_genre = exploded[exploded['genres'] == selected_genre]
        top_genre = top_genre.sort_values(by='numVotes', ascending=False).drop_duplicates('title')
        top_genre['rating'] = top_genre['rating'].map(lambda x: f"{x:.1f}")
        top_genre_display = top_genre[['title', 'year', 'rating', 'numVotes']].head(10)
        st.table(top_genre_display)

# --- Entry Point ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    login_page()
else:
    main_dashboard()