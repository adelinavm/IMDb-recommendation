git fetch origingit log origin/main --onelinegit log origin/main --onelineimport requests
import pandas as pd
import time

# Konfigurasi RapidAPI
API_KEY = "68ed4b1c1fmsha3517c06d7ee2f0p1237fejsn1a401a6c4f5d"
API_HOST = "imdb8.p.rapidapi.com"

# Fungsi ambil detail film dari 3 endpoint
def get_film_details_multi(tconst):
    base_url = "https://imdb8.p.rapidapi.com/title/v2/"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }

    def safe_json(url, key):
        try:
            res = requests.get(url, headers=headers, params={"tconst": tconst})
            return res.json().get("data", {})
        except:
            print(f"⚠️ Gagal parsing {key} untuk {tconst}")
            return {}

    # Title & Year
    detail_data = safe_json(base_url + "get-details", "details")
    title_info = detail_data.get("title", {})
    title = title_info.get("titleText", {}).get("text", "N/A")
    year = title_info.get("releaseYear", {}).get("year", "N/A")

    # Genres
    genres_data = safe_json(base_url + "get-genres", "genres")
    genre_items = genres_data.get("title", {}).get("titleGenres", {}).get("genres", [])
    genres = ", ".join([g["genre"]["text"] for g in genre_items]) if genre_items else "N/A"

    # Ratings
    ratings_data = safe_json(base_url + "get-ratings", "ratings")
    ratings_summary = ratings_data.get("title", {}).get("ratingsSummary", {})
    rating = ratings_summary.get("aggregateRating", "N/A")
    vote_count = ratings_summary.get("voteCount", 0)

    return {
        "tconst": tconst,
        "title": title,
        "year": year,
        "genres": genres,
        "rating": rating,
        "numVotes": vote_count
    }

# Step 1: Load ID dari file sumber dan data sudah ada
id_df = pd.read_csv("top250_imdb_ids.csv")
all_ids = set(id_df["tconst"])

try:
    completed_df = pd.read_csv("film_detail_complete.csv")
    completed_ids = set(completed_df["tconst"])
except:
    completed_df = pd.DataFrame()
    completed_ids = set()

# Step 2: Cari ID yang belum diambil atau datanya masih N/A
incomplete_ids = set()
if not completed_df.empty:
    incomplete_df = completed_df[
        (completed_df['title'] == "N/A") |
        (completed_df['genres'] == "N/A") |
        (completed_df['rating'] == "N/A") |
        (completed_df["numVotes"] == 0)
    ]
    incomplete_ids = set(incomplete_df["tconst"])
    print(f"🔍 Total baris gagal: {len(incomplete_df)}")

# ID yang benar-benar perlu di-fetch ulang
remaining_ids = list((all_ids - completed_ids) | incomplete_ids)
print(f"🎯 Total ID yang akan difetch ulang: {len(remaining_ids)}")

# Step 3: Ambil data untuk sisa ID
new_data = []

for i, fid in enumerate(remaining_ids):
    try:
        print(f"📥 [{i+1}/{len(remaining_ids)}] Ambil: {fid}")
        new_data.append(get_film_details_multi(fid))
        time.sleep(1)
    except Exception as e:
        print(f"❌ Error {fid}: {e}")

# Step 4: Gabungkan data baru dengan yang lama
new_df = pd.DataFrame(new_data)
if not completed_df.empty:
    combined = pd.concat([
        completed_df[~completed_df["tconst"].isin(remaining_ids)],
        new_df
    ], ignore_index=True)
else:
    combined = new_df

combined.to_csv("film_detail_complete_fixed.csv", index=False)
print("✅ Data lengkap dan sudah diperbaiki disimpan ke 'film_detail_complete_fixed.csv'")
