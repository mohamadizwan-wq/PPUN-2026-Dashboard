import streamlit as st
import pandas as pd
import datetime
import re
import time
import os

# ==========================================
# LINK GOOGLE SHEET 
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/103YxYTV0SECLCN7lkbWCVph8wRzVxqoPZozLb8d9Lc0/edit?gid=0#gid=0"

st.set_page_config(page_title="Dashboard Eksekutif PPUN", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        .stApp { background-color: #F3F4F6; }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        [data-testid="stSidebar"] { background-color: #0F172A; color: white; }
        [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
        
        .exec-header {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            padding: 25px 40px; border-radius: 16px; border-left: 8px solid #D4AF37;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 30px; margin-top: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .exec-title h1 { color: #FFFFFF !important; font-size: 30px; font-weight: 800; margin: 0; letter-spacing: -0.5px;}
        .exec-title p { color: #94A3B8 !important; font-size: 14px; margin: 8px 0 0 0; font-weight: 500; }
        
        .kpi-wrapper { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .kpi-card {
            flex: 1; min-width: 230px; background: #FFFFFF; padding: 25px; border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #E2E8F0;
        }
        .kpi-title { color: #64748B; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
        .kpi-value { color: #0F172A; font-size: 36px; font-weight: 800; margin-top: 10px; }
        .val-siap { color: #059669; }
        .val-proses { color: #D97706; }

        .proj-card {
            background: white; border-radius: 12px; padding: 20px;
            border: 1px solid #E2E8F0; border-top: 4px solid #1E293B; margin-bottom: 20px;
        }
        .proj-title { color: #0F172A; font-size: 18px; font-weight: 700; margin-bottom: 5px; }
        .proj-agency { color: #64748B; font-size: 14px; font-weight: 500; margin-bottom: 15px;}
        
        .badge { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
        .b-siap { background: #D1FAE5; color: #065F46; border: 1px solid #34D399; }
        .b-proses { background: #FEF3C7; color: #92400E; border: 1px solid #FBBF24; }
        .b-lewat { background: #FEE2E2; color: #991B1B; border: 1px solid #F87171; }
        hr { border-color: #E2E8F0; margin: 15px 0; }
    </style>
""", unsafe_allow_html=True)

def dapatkan_link_gambar(url):
    if pd.isna(url) or url == "-": return None
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', str(url)) or re.search(r'id=([a-zA-Z0-9_-]+)', str(url))
    if match: return f"https://drive.google.com/uc?export=view&id={match.group(1)}"
    return str(url)

def bina_link_live(url):
    if "export?format=csv" in url: return f"{url}&t={time.time()}"
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if match:
        file_id = match.group(1)
        gid_match = re.search(r'[#&?]gid=([0-9]+)', url)
        gid = f"&gid={gid_match.group(1)}" if gid_match else ""
        return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv{gid}&t={time.time()}"
    return url

@st.cache_data(ttl=1)
def load_data(url):
    try:
        live_url = bina_link_live(url)
        df = pd.read_csv(live_url, skiprows=1)
        df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed')]
        df = df.dropna(how='all').fillna("-")
        if 'Bil.' in df.columns:
            df['Bil.'] = pd.to_numeric(df['Bil.'], errors='coerce').fillna(0).astype(int).astype(str)
            df['Bil.'] = df['Bil.'].replace('0', '-')
        return df
    except Exception as e:
        return pd.DataFrame()

with st.spinner('Menyegerak pangkalan data MOTAC...'):
    df = load_data(SHEET_URL)

if not df.empty:
    
    # ==========================
    # MENU KIRI (SIDEBAR) & LOGO MADANI
    # ==========================
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>⚙️ Panel Kawalan</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size:13px;'>Tapis data projek di sini</p><hr style='border-color:#334155;'>", unsafe_allow_html=True)
        
        senarai_agensi = ["Semua Agensi"] + list(df['Agensi Pelaksana'].unique()) if 'Agensi Pelaksana' in df.columns else ["Semua Agensi"]
        senarai_agensi = [x for x in senarai_agensi if x != "-"]
        
        carian_teks = st.text_input("🔍 Cari Projek / Kontraktor:")
        pilih_agensi = st.selectbox("🏢 Pilih Agensi:", senarai_agensi)
        pilih_status = st.selectbox("📊 Status Projek:", ["Semua Status", "Telah Siap", "Dalam Pelaksanaan", "Lain-lain"])
        
        st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)
        if st.button("🔄 *Refresh*", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        
        # Susun Logo Madani di Bawah Kiri (Sidebar)
        col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
        for ext in ['.png', '.jpg', '.jpeg']:
            if os.path.exists(f"madani{ext}"):
                with col_m2:
                    st.image(f"madani{ext}", use_container_width=True)
                break
                
        st.markdown("<div style='margin-top:10px; text-align:center; font-size:12px; color:#94A3B8;'>Sistem Pemantauan V2.0<br>© 2026 MOTAC</div>", unsafe_allow_html=True)

    # Logik Tapisan
    df_tapis = df.copy()
    if carian_teks:
        mask = pd.Series([False] * len(df_tapis))
        for col in df_tapis.columns: mask = mask | df_tapis[col].astype(str).str.contains(carian_teks, case=False, na=False)
        df_tapis = df_tapis[mask]
    if pilih_agensi != "Semua Agensi": df_tapis = df_tapis[df_tapis['Agensi Pelaksana'] == pilih_agensi]
    if pilih_status != "Semua Status":
        if pilih_status == "Telah Siap": df_tapis = df_tapis[df_tapis['Status Semasa'].astype(str).str.contains("Siap|Selesai", case=False, na=False)]
        elif pilih_status == "Dalam Pelaksanaan": df_tapis = df_tapis[df_tapis['Status Semasa'].astype(str).str.contains("Proses|Progress|Laksana|Sedang", case=False, na=False)]

    jumlah_projek = len(df)
    siap = df[df['Status Semasa'].astype(str).str.contains("Siap|Selesai", case=False, na=False)].shape[0] if 'Status Semasa' in df.columns else 0
    proses = df[df['Status Semasa'].astype(str).str.contains("Proses|Progress|Laksana|Sedang", case=False, na=False)].shape[0] if 'Status Semasa' in df.columns else 0

    # ==========================
    # LOGO JATA & JABATAN (ATAS KIRI MAIN PAGE)
    # ==========================
    col_img1, col_img2, col_kosong = st.columns([1, 1, 10])
    
    def papar_logo(nama_fail, kolum):
        for ext in ['.png', '.jpg', '.jpeg']:
            if os.path.exists(f"{nama_fail}{ext}"):
                with kolum:
                    st.image(f"{nama_fail}{ext}", width=80)
                break
                
    papar_logo("jata", col_img1)
    papar_logo("jabatan", col_img2)

    # ==========================
    # BANNER UTAMA
    # ==========================
    masa_kini = datetime.datetime.now().strftime('%d/%m/%Y, %I:%M %p')
    st.markdown(f"""
        <div class="exec-header">
            <div class="exec-title">
                <h1>DASHBOARD EKSEKUTIF PPUN</h1>
                <p>Pemantauan Projek Infrastruktur Pelancongan | Dikemaskini: {masa_kini}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="kpi-wrapper">
            <div class="kpi-card">
                <div class="kpi-title">📋 Jumlah Projek Didaftarkan</div>
                <div class="kpi-value">{jumlah_projek}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">🚧 Sedang Dalam Pelaksanaan</div>
                <div class="kpi-value val-proses">{proses}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">✅ Projek Telah Siap</div>
                <div class="kpi-value val-siap">{siap}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 📑 Hasil Carian: {len(df_tapis)} Projek Rekod Ditemui")
    st.write("")

    if not df_tapis.empty:
        for idx, row in df_tapis.iterrows():
            stat_text = str(row.get('Status Semasa', '-'))
            if "siap" in stat_text.lower() or "selesai" in stat_text.lower(): badge_html = f"<span class='badge b-siap'>✓ {stat_text.upper()}</span>"
            elif "proses" in stat_text.lower() or "laksana" in stat_text.lower() or "sedang" in stat_text.lower(): badge_html = f"<span class='badge b-proses'>⏳ {stat_text.upper()}</span>"
            else: badge_html = f"<span class='badge b-lewat'>⚠️ {stat_text.upper()}</span>"

            with st.container():
                st.markdown(f"""
                <div class="proj-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div class="proj-title">#{row.get('Bil.', '-')} {row.get('Tajuk Program', '-')}</div>
                            <div class="proj-agency">🏢 {row.get('Agensi Pelaksana', '-')}</div>
                        </div>
                        <div>{badge_html}</div>
                    </div>
                    <hr>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1.5, 1, 1])
                with col1:
                    st.markdown("**📌 Skop Kerja Utama:**")
                    st.info(row.get('Skop Kerja', '-'))
                with col2:
                    st.markdown("**💰 Kewangan & Tempoh:**")
                    st.write(f"**Peruntukan:** {row.get('Peruntukkan', '-')}")
                    st.write(f"**Kos Projek:** {row.get('Kos Projek', '-')}")
                    st.write(f"**Mula:** {row.get('Tarikh Mula', '-')}")
                    st.write(f"**Siap:** {row.get('Tarikh Siap', '-')}")
                with col3:
                    st.markdown("**👷🏻‍♂️ Pelaksanaan:**")
                    st.write(f"**Kontraktor:** {row.get('Kontraktor', '-')}")
                    st.write(f"**Kemajuan:** {row.get('Peratus Siap Kerja', '-')}")
                    
                    gambar_url = dapatkan_link_gambar(row.get('Gambar Projek', '-'))
                    if gambar_url and "http" in gambar_url: st.image(gambar_url, caption="Visual Terkini", use_container_width=True)
                    else: st.caption("📷 *Tiada visual dimuat naik*")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Tiada rekod projek yang sepadan dengan carian/tapisan anda.")

else:
    st.error("Gagal menarik data. Pastikan Google Sheet diset kepada 'Anyone with the link' (Viewer).")
