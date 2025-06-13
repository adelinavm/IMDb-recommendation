import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import os
import plotly.express as px
from auth_utils import authenticate_user, register_user
import sidebar

def load_data():
    df = pd.read_csv("film_detail_complete_fixed.csv")
    df = df.dropna(subset=['title', 'genres', 'rating'])
    df = df[df['title'] != "N/A"]
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])
    df['rating'] = df['rating'].astype(float)
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

    # --- Mood & Genre Recommendation ---
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
    # Dropdown genre dari seluruh genre unik
    all_genres = sorted(set(g for sublist in rekom_df['genres'].str.split(', ') for g in sublist))
    user_genre = st.selectbox("(Opsional) Tambah Genre Favoritmu", [""] + all_genres)
    target_genres = mood_map[mood].copy()
    if user_genre:
        target_genres.append(user_genre)
    exploded = rekom_df.copy()
    exploded['genres'] = exploded['genres'].str.split(", ")
    exploded = exploded.explode('genres')
    recommend = exploded[exploded['genres'].isin(target_genres)]
    recommend = recommend.sort_values(by="rating", ascending=False).drop_duplicates("title")
    if not recommend.empty:
        recommend = recommend.copy()
        recommend['year'] = recommend['year'].astype(int)
        recommend['rating'] = recommend['rating'].astype(float).round(1)
        st.markdown(f"Top rekomendasi untuk mood **{mood}**{f' & genre **{user_genre}**' if user_genre else ''}:")
        st.table(recommend[['title', 'year', 'genres', 'rating']].head(10))
    else:
        st.info("Tidak ada rekomendasi untuk mood/genre tersebut.")
    # --- Trending Movies This Year (Bar Chart) ---
    st.subheader("🔥 Film Trending Tahun Ini")
    latest_year = int(df['year'].max())
    top_year = df[df['year'] == latest_year]
    top_year = top_year.sort_values(by='numVotes', ascending=False)
    top_year['year'] = top_year['year'].astype(int)
    top_year['rating'] = top_year['rating'].astype(float).round(1)
    fig_trend = px.bar(
        top_year.head(10),
        x='title',
        y='numVotes',
        color='rating',
        hover_data={'title': True, 'rating': ':.1f', 'numVotes': ':,'},
        labels={'title': 'Judul Film', 'numVotes': 'Jumlah Suara', 'rating': 'Rating'},
        title=f'Film dengan suara terbanyak di tahun {latest_year}'
    )
    fig_trend.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_trend, use_container_width=True)
    # --- Trend Visualization (Line Chart) ---
    st.header("📈 Tren Film Saat Ini")
    latest_year = int(exploded['year'].max())
    trend_data = exploded[exploded['year'] >= latest_year - 5]
    trend = trend_data.groupby(['year', 'genres']).size().reset_index(name='count')
    trend['year'] = trend['year'].astype(int)
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
        hover_data={'genres': True, 'count': ':,', 'year': ':d'},
        labels={'count': 'Jumlah Film', 'year': 'Tahun', 'genres': 'Genre'},
        title='Jumlah Film per Genre (5 Tahun Terakhir)'
    )
    st.plotly_chart(fig2, use_container_width=True)
    if selected_genre != "Semua Genre":
        st.subheader(f"🏆 Top 10 Film Terlaris dalam Genre '{selected_genre}'")
        top_genre = exploded[exploded['genres'] == selected_genre]
        top_genre = top_genre.sort_values(by='numVotes', ascending=False).drop_duplicates('title')
        top_genre['year'] = top_genre['year'].astype(int)
        top_genre['rating'] = top_genre['rating'].astype(float).round(1)
        top_genre['numVotes'] = top_genre['numVotes'].astype(int)
        top_genre_display = top_genre[['title', 'year', 'rating', 'numVotes']].head(10)
        st.table(top_genre_display)
    # --- Rata-Rata Rating per Genre (Bar Chart Horizontal) ---
    st.header("📊 Rata-Rata Rating per Genre")
    genre_rating = exploded.groupby('genres')['rating'].mean().sort_values(ascending=False).reset_index()
    genre_rating['rating'] = genre_rating['rating'].astype(float).round(2)
    if exploded.empty or genre_rating.empty:
        st.warning("Data tidak tersedia untuk visualisasi genre.")
    else:
        fig = px.bar(
            genre_rating,
            x='rating',
            y='genres',
            orientation='h',
            color='rating',
            color_continuous_scale='viridis',
            hover_data={'genres': True, 'rating': ':.2f'},
            labels={'rating': 'Rata-Rata Rating', 'genres': 'Genre'},
            title='Rata-Rata Rating per Genre'
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

# --- App Entry Point ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    login_page()
else:
    main_dashboard()
