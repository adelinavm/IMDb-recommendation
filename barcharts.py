# Trending Movies This Year
st.subheader("🔥 Film Trending Tahun Ini")

latest_year = df['year'].max()
top_year = df[df['year'] == latest_year]
top_year = top_year.sort_values(by='numVotes', ascending=False)

fig_trend = px.bar(
    top_year.head(10),
    x='title',
    y='numVotes',
    color='rating',
    hover_data=['title', 'rating', 'numVotes'],
    labels={'title': 'Judul Film', 'numVotes': 'Jumlah Suara', 'rating': 'Rating'},
    title=f'Film dengan suara terbanyak di tahun {int(latest_year)}'
)
fig_trend.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_trend, use_container_width=True)