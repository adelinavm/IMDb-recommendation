# Visualisasi tren film sekarang (jumlah film per genre per tahun)
st.subheader("📈 Tren Film Saat Ini")

trend_data = exploded[exploded['year'] >= latest_year - 5]  # 5 tahun terakhir
trend = trend_data.groupby(['year', 'genres']).size().reset_index(name='count')

# Dropdown untuk memilih genre
all_genres = sorted(trend['genres'].unique())
selected_genre = st.selectbox("Pilih Genre", ["Semua Genre"] + all_genres)

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

# Top 10 Film Terlaris berdasarkan genre yang dipilih
if selected_genre != "Semua Genre":
    st.subheader(f"🏆 Top 10 Film Terlaris dalam Genre '{selected_genre}'")

    top_genre = exploded[exploded['genres'] == selected_genre]
    top_genre = top_genre.sort_values(by='numVotes', ascending=False).drop_duplicates('title')
    top_genre['year'] = top_genre['year'].astype(int)
    top_genre['rating'] = top_genre['rating'].astype(float).round(1)

    top_genre_display = top_genre[['title', 'year', 'rating', 'numVotes']].head(10)
    st.table(top_genre_display)


# Footer
st.markdown("---")
st.caption("Built with ❤️ by 1 Adik 4 Kakak")