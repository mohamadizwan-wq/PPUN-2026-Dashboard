import streamlit as st
import pandas as pd
import datetime

# --- TUKAR LINK INI DENGAN LINK CSV PUBLISH TO WEB ANDA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZ6tx2sYh-Qo6_oTTjj4cmPqi4ID3v_wQSqGumh5rLekMCe25IwRkEXEb9LS0hB1B9zRW0RcSaG84W/pub?gid=0&single=true&output=csv"

# Konfigurasi Halaman (Mesti di baris atas sekali)
st.set_page_config(page_title="Dashboard Projek PPUN", page_icon="🏢", layout="wide")

# CSS Tambahan untuk bagi nampak lebih kemas
st.markdown("""
<style>
    .stMetric { background-color: #F8FAFC; padding: 15px; border-radius: 8px; border-left: 5px solid #17365D; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .css-1d391kg { padding-top: 2rem; }
    h1 { color: #17365D; border-bottom: 3px solid #D4AF37; padding-bottom: 10px; margin-bottom: 20px;}
    .badge-siap { background-color: #DCFCE7; color: #166534; padding: 4px 8px; border-radius: 12px; font-size: 14px; font-weight: bold;}
    .badge-proses { background-color: #FEF9C3; color: #854D0E; padding: 4px 8px; border-radius: 12px; font-size: 14px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# Tajuk
st.title("Dashboard Pemantauan Projek PPUN (MOTAC)")
st.write(f"**Data dikemaskini pada:** {datetime.datetime.now().strftime('%d/%m/%Y %I:%M %p')}")

# Fungsi untuk load data (Cache supaya tak berat)
@st.cache_data(ttl=60) # Cache tahan 60 saat sebelum tarik data baru
def load_data(url):
    try:
        # Pandas boleh terus baca link CSV
        df = pd.read_csv(url)
        
        # Bersihkan data (buang baris yang semua kolum kosong)
        df = df.dropna(how='all')
        
        # Isi NaN dengan string kosong supaya kemas
        df = df.fillna("")
        
        return df
    except Exception as e:
        st.error(f"Gagal memuat turun data. Sila semak link Google Sheet. Ralat: {e}")
        return pd.DataFrame()

# Muat data
with st.spinner('Sedang menarik data dari Google Sheet...'):
    df = load_data(SHEET_URL)

if not df.empty:
    
    # 1. Bahagian Metrik (Statistik)
    col1, col2, col3 = st.columns(3)
    
    jumlah_projek = len(df)
    # Andaikan kolum status bernama 'Status Semasa'. Tukar nama kolum ini jika berbeza dalam Sheet anda.
    if 'Status Semasa' in df.columns:
        status_siap = df[df['Status Semasa'].str.contains("Siap|Selesai", case=False, na=False)].shape[0]
        status_proses = df[df['Status Semasa'].str.contains("Proses|Progress|Laksana", case=False, na=False)].shape[0]
    else:
        status_siap = 0
        status_proses = 0

    col1.metric("Jumlah Projek", jumlah_projek)
    col2.metric("Telah Siap", status_siap)
    col3.metric("Dalam Pelaksanaan", status_proses)
    
    st.markdown("---")

    # 2. Bahagian Carian
    carian = st.text_input("🔍 Cari Projek (Nama / Agensi / Kontraktor):", "")
    
    # Tapis data berdasarkan carian
    if carian:
        # Buat carian di semua kolum utama
        mask = pd.Series([False] * len(df))
        for col in ['Tajuk Program', 'Agensi Pelaksana', 'Kontraktor', 'Status Semasa']:
            if col in df.columns:
                mask = mask | df[col].astype(str).str.contains(carian, case=False, na=False)
        df_dipapar = df[mask]
    else:
        df_dipapar = df

    # 3. Papar Jadual
    if not df_dipapar.empty:
        # Buang kolum Gambar Projek untuk paparan jadual pandas biasa jika mahu nampak kemas
        # Tapi kita paparkan semua buat masa ini.
        st.dataframe(
            df_dipapar,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Tiada projek dijumpai untuk carian tersebut.")

   # 4. Butang Refresh Manual (Pilihan)
    if st.button("*Refresh* 🔄"):
        st.cache_data.clear() # Kosongkan cache
        st.rerun() # Reload app

else:
    st.warning("Data projek kosong atau tidak dijumpai.")
