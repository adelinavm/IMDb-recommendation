# Genre vs Rating (Interactive)
st.subheader("📊 Rata-Rata Rating per Genre (Interaktif)")

exploded = df.copy()
exploded['genres'] = exploded['genres'].str.split(", ")
exploded = exploded.explode('genres')

genre_rating = exploded.groupby('genres')['rating'].mean().sort_values(ascending=False).reset_index()

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

# Mood-based Recommendation
st.subheader("🤖 Rekomendasi Film Berdasarkan Mood & Genre")

# Update mood options
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

recommend = exploded[exploded['genres'].isin(target_genres)]
recommend = recommend.sort_values(by="rating", ascending=False).drop_duplicates("title")