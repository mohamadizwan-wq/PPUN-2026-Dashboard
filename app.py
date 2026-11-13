import streamlit as st
import pandas as pd
import datetime
import re

# ==========================================
# MASUKKAN LINK CSV PUBLISH TO WEB DI SINI
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZ6tx2sYh-Qo6_oTTjj4cmPqi4ID3v_wQSqGumh5rLekMCe25IwRkEXEb9LS0hB1B9zRW0RcSaG84W/pub?gid=0&single=true&output=csv"

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Sistem Pemantauan Projek PPUN", page_icon="🏢", layout="wide")

# 2. CSS untuk jadikan butang dan kad lebih premium
st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; }
        .corporate-header {
            background-color: #17365D; padding: 25px; border-radius: 10px;
            border-bottom: 5px solid #D4AF37; margin-bottom: 25px; margin-top: -40px; color: white;
        }
        .corporate-header h1 { font-size: 28px; margin: 0; color: white !important;}
        .corporate-header p { margin: 5px 0 0 0; font-size: 14px; color: #CBD5E1 !important;}
        .project-card {
            background: white; padding: 20px; border-radius: 10px;
            border: 1px solid #E2E8F0; border-left: 5px solid #17365D;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;
        }
        .badge-siap { background: #DCFCE7; color: #166534; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
        .badge-proses { background: #FEF9C3; color: #854D0E; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
        .badge-lewat { background: #FEE2E2; color: #991B1B; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. Header Korporat
masa_kini = datetime.datetime.now().strftime('%d/%m/%Y %I:%M %p')
st.markdown(f"""
    <div class="corporate-header">
        <h1>🏢 Sistem Pemantauan Projek PPUN (MOTAC)</h1>
        <p>Data dikemaskini secara langsung | {masa_kini}</p>
    </div>
""", unsafe_allow_html=True)

# 4. Fungsi menukar link Google Drive kepada imej yang boleh dipapar
def dapatkan_link_gambar(url):
    if pd.isna(url) or url == "-":
        return None
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', str(url)) or re.search(r'id=([a-zA-Z0-9_-]+)', str(url))
    if match:
        return f"https://drive.google.com/uc?export=view&id={match.group(1)}"
    return str(url)

# 5. Fungsi Load Data
@st.cache_data(ttl=30)
def load_data(url):
    try:
        df = pd.read_csv(url, skiprows=1)
        df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
        df = df.dropna(how='all').fillna("-")
        
        # Bersihkan nombor 'Bil.' supaya tak jadi 1.0, 2.0
        if 'Bil.' in df.columns:
            df['Bil.'] = pd.to_numeric(df['Bil.'], errors='coerce').fillna(0).astype(int).astype(str)
            df['Bil.'] = df['Bil.'].replace('0', '-')
            
        return df
    except Exception as e:
        return pd.DataFrame()

with st.spinner('Menarik data dari Google Sheet...'):
    df = load_data(SHEET_URL)

if not df.empty:
    # 6. Sistem Filter (Dropdown)
    st.subheader("🔍 Carian & Tapisan")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    # Dapatkan senarai unik untuk Dropdown
    senarai_agensi = ["Semua Agensi"] + list(df['Agensi Pelaksana'].unique()) if 'Agensi Pelaksana' in df.columns else ["Semua Agensi"]
    senarai_agensi = [x for x in senarai_agensi if x != "-"]
    
    with col_f1:
        carian_teks = st.text_input("Cari Tajuk / Skop Kerja:")
    with col_f2:
        pilih_agensi = st.selectbox("Pilih Agensi:", senarai_agensi)
    with col_f3:
        pilih_status = st.selectbox("Status Semasa:", ["Semua Status", "Telah Siap", "Dalam Pelaksanaan", "Lain-lain"])

    # Logik Tapisan Data
    df_tapis = df.copy()
    
    if carian_teks:
        mask = pd.Series([False] * len(df_tapis))
        for col in df_tapis.columns:
            mask = mask | df_tapis[col].astype(str).str.contains(carian_teks, case=False, na=False)
        df_tapis = df_tapis[mask]
        
    if pilih_agensi != "Semua Agensi":
        df_tapis = df_tapis[df_tapis['Agensi Pelaksana'] == pilih_agensi]
        
    if pilih_status != "Semua Status":
        if pilih_status == "Telah Siap":
            df_tapis = df_tapis[df_tapis['Status Semasa'].astype(str).str.contains("Siap|Selesai", case=False, na=False)]
        elif pilih_status == "Dalam Pelaksanaan":
            df_tapis = df_tapis[df_tapis['Status Semasa'].astype(str).str.contains("Proses|Progress|Laksana", case=False, na=False)]

    st.write("---")
    st.subheader(f"📋 Senarai Projek ({len(df_tapis)} rekod ditemui)")

    # 7. Paparan Data Bentuk Kad & Gambar (Bukan Jadual Bosan)
    if not df_tapis.empty:
        for idx, row in df_tapis.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="project-card">
                    <h4 style="color:#17365D; margin-bottom:5px;">#{row.get('Bil.', '-')} - {row.get('Tajuk Program', '-')}</h4>
                    <p style="color:#64748B; font-size:14px; margin-top:0;"><strong>Agensi:</strong> {row.get('Agensi Pelaksana', '-')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Buka expander untuk detail & gambar
                with st.expander("Klik untuk lihat perincian & gambar projek"):
                    detail_col1, detail_col2 = st.columns([2, 1])
                    
                    with detail_col1:
                        st.markdown(f"**Skop Kerja:**\n{row.get('Skop Kerja', '-')}")
                        st.markdown(f"**Kontraktor:** {row.get('Kontraktor', '-')}")
                        st.markdown(f"**Peruntukan:** {row.get('Peruntukkan', '-')} | **Kos Projek:** {row.get('Kos Projek', '-')}")
                        st.markdown(f"**Tarikh:** {row.get('Tarikh Mula', '-')} hingga {row.get('Tarikh Siap', '-')}")
                        
                        # Formatting status text
                        stat_text = str(row.get('Status Semasa', '-'))
                        if "siap" in stat_text.lower():
                            st.markdown(f"**Status Semasa:** <span class='badge-siap'>{stat_text}</span>", unsafe_allow_html=True)
                        elif "proses" in stat_text.lower() or "laksana" in stat_text.lower():
                            st.markdown(f"**Status Semasa:** <span class='badge-proses'>{stat_text}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**Status Semasa:** <span class='badge-lewat'>{stat_text}</span>", unsafe_allow_html=True)
                            
                        st.markdown(f"**Kemajuan Kerja:** {row.get('Peratus Siap Kerja', '-')}")

                    with detail_col2:
                        gambar_url = dapatkan_link_gambar(row.get('Gambar Projek', '-'))
                        if gambar_url and "http" in gambar_url:
                            st.image(gambar_url, caption="Gambar Tapak Projek", use_container_width=True)
                        else:
                            st.info("Tiada gambar dimuat naik.")
    else:
        st.warning("Tiada rekod projek yang sepadan dengan carian/tapisan anda.")

    st.write("")
    if st.button("*Refresh* Data 🔄"):
        st.cache_data.clear()
        st.rerun()

else:
    st.error("Gagal menarik data. Sila pastikan link CSV Google Sheet dimasukkan dengan betul.")
