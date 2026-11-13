import streamlit as st
import pandas as pd
import datetime

# --- TUKAR LINK INI DENGAN LINK CSV PUBLISH TO WEB ANDA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZ6tx2sYh-Qo6_oTTjj4cmPqi4ID3v_wQSqGumh5rLekMCe25IwRkEXEb9LS0hB1B9zRW0RcSaG84W/pub?gid=0&single=true&output=csv"

# 1. Konfigurasi Halaman (Mesti di baris atas sekali)
st.set_page_config(page_title="Dashboard Projek PPUN", page_icon="🏢", layout="wide")

# 2. Suntikan CSS Korporat MOTAC
st.markdown("""
    <style>
        .stApp { background-color: #F1F5F9; }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        
        .corporate-header {
            background-color: #17365D;
            padding: 30px;
            border-radius: 12px;
            border-bottom: 5px solid #D4AF37;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            margin-bottom: 25px;
            margin-top: -40px;
        }
        .corporate-header h1 { color: #FFFFFF !important; font-size: 32px; font-weight: bold; margin: 0; font-family: 'Arial', sans-serif;}
        .corporate-header p { color: #CBD5E1 !important; font-size: 15px; margin-top: 5px; }

        div[data-testid="metric-container"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 6px solid #17365D;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        div[data-testid="metric-container"] label { color: #64748B !important; font-weight: bold; font-size: 14px; text-transform: uppercase; }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #17365D !important; font-weight: bold; font-size: 36px; }

        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
            font-family: 'Arial', sans-serif;
            background-color: #ffffff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            border-radius: 10px;
            overflow: hidden;
        }
        .styled-table thead tr { background-color: #17365D; color: #ffffff; text-align: left; }
        .styled-table th, .styled-table td { padding: 15px; }
        .styled-table tbody tr { border-bottom: 1px solid #dddddd; }
        .styled-table tbody tr:nth-of-type(even) { background-color: #F8FAFC; }
        .styled-table tbody tr:hover { background-color: #F1F5F9; }
    </style>
""", unsafe_allow_html=True)

# 3. Banner Tajuk Dashboard
masa_kini = datetime.datetime.now().strftime('%d/%m/%Y %I:%M %p')
st.markdown(f"""
    <div class="corporate-header">
        <h1>🏢 Dashboard Pemantauan Projek PPUN</h1>
        <p>Kementerian Pelancongan, Seni dan Budaya (MOTAC) | Data Terkini: {masa_kini}</p>
    </div>
""", unsafe_allow_html=True)

# 4. Fungsi Load Data dari Sheet (Dibaiki sepenuhnya)
@st.cache_data(ttl=30)
def load_data(url):
    try:
        # skiprows=1 akan abaikan tajuk besar "ROJEK DI BAWAH PERUNTUKAN..." di baris 1
        df = pd.read_csv(url, skiprows=1)
        
        # Buang lajur-lajur rosak bernama 'Unnamed'
        df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
        
        # Buang baris yang kosong & tukar NaN jadi "-"
        df = df.dropna(how='all').fillna("-") 
        
        return df
    except Exception as e:
        return pd.DataFrame()

with st.spinner('Sedang menarik data dari pelayan...'):
    df = load_data(SHEET_URL)

if not df.empty:
    
    # 5. Bahagian Statistik
    col1, col2, col3 = st.columns(3)
    
    if 'Status Semasa' in df.columns:
        siap = df[df['Status Semasa'].astype(str).str.contains("Siap|Selesai", case=False, na=False)].shape[0]
        proses = df[df['Status Semasa'].astype(str).str.contains("Proses|Progress|Laksana|Sedang", case=False, na=False)].shape[0]
    else:
        siap, proses = 0, 0

    col1.metric("📊 Jumlah Projek", len(df))
    col2.metric("✅ Telah Siap", siap)
    col3.metric("🚧 Dalam Pelaksanaan", proses)
    
    st.write("---")

    # 6. Kotak Carian
    carian = st.text_input("🔍 Carian Pantas (Taip nama projek, agensi, atau kontraktor):", "")
    
    if carian:
        mask = pd.Series([False] * len(df))
        for col in df.columns:
            mask = mask | df[col].astype(str).str.contains(carian, case=False, na=False)
        df_dipapar = df[mask]
    else:
        df_dipapar = df

    # 7. Render Jadual menggunakan HTML
    if not df_dipapar.empty:
        html_table = df_dipapar.to_html(classes="styled-table", index=False, escape=False)
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.info("Tiada rekod dijumpai.")

    st.write("")
    
    # 8. Butang Refresh
    if st.button("*Refresh* 🔄"):
        st.cache_data.clear()
        st.rerun()

else:
    st.error("Gagal menarik data. Sila pastikan link CSV Google Sheet dimasukkan dengan betul.")
