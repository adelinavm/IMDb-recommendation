import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Path ke file CSV (otomatis, relatif terhadap file ini)
CSV_PATH = os.path.join(os.path.dirname(__file__), 'film_detail_complete_fixed.csv')

st.set_page_config(layout="wide")

def load_data():
    df = pd.read_csv(CSV_PATH)
    df = df.dropna(subset=['title', 'genres', 'rating'])
    df = df[df['title'] != "N/A"]
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])
    df['rating'] = df['rating'].astype(float)
    return df

def main():
    df = load_data()
    st.title("📊 Rata-Rata Rating per Genre")
    exploded = df.copy()
    exploded['genres'] = exploded['genres'].str.split(", ")
    exploded = exploded.explode('genres')
    genre_rating = exploded.groupby('genres')['rating'].mean().sort_values(ascending=False).reset_index()
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

if __name__ == "__main__":
    main()
