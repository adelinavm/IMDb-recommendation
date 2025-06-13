# IMDb-recommendation

# --- Auth Section ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''

def show_login():
    st.title("🎬 IMDb Movie Dashboard - 1 Adik 4 Kakak")
    st.header("Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign In"):
        if authenticate_user(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"Selamat datang, {username}!")
            st.rerun()
        else:
            st.error("Username atau password salah.")
    st.markdown("Belum punya akun?")
    if st.button("Register"):
        st.session_state['show_register'] = True
        st.rerun()

def show_register():
    st.title("🎬 IMDb Movie Dashboard - 1 Adik 4 Kakak")
    st.header("Register Akun Baru")
    username = st.text_input("Username Baru")
    password = st.text_input("Password Baru", type="password")
    password2 = st.text_input("Konfirmasi Password", type="password")
    if st.button("Register Akun"):
        if not username or not password:
            st.warning("Username dan password wajib diisi.")
        elif password != password2:
            st.warning("Password tidak cocok.")
        else:
            ok, msg = register_user(username, password)
            if ok:
                st.success(msg)
                st.session_state['show_register'] = False
                st.rerun()
            else:
                st.error(msg)
    if st.button("Kembali ke Login"):
        st.session_state['show_register'] = False
        st.rerun()

if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False

if not st.session_state['logged_in']:
    if st.session_state['show_register']:
        show_register()
    else:
        show_login()
    st.stop()

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("film_detail_complete_fixed.csv")
    df = df.dropna(subset=['title', 'genres', 'rating'])  # Hapus baris kosong
    df = df[df['title'] != "N/A"]
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')  # Pastikan rating numerik
    df = df.dropna(subset=['rating'])  # Hapus rating yang gagal dikonversi
    df['rating'] = df['rating'].astype(float)
    return df

df = load_data()