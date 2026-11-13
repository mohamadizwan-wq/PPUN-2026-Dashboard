import streamlit as st
import pandas as pd
import re
import time
import os
import base64

# ==========================================
# LINK GOOGLE SHEET 
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/103YxYTV0SECLCN7lkbWCVph8wRzVxqoPZozLb8d9Lc0/edit?gid=0#gid=0"

# Set layout kepada "wide"
st.set_page_config(page_title="Dashboard Eksekutif PPUN", page_icon="📈", layout="wide")

# CSS Paksaan Full Screen & Design
st.markdown("""
    <style>
        .block-container {
            max-width: 100% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-top: 2rem !important;
        }

        .stApp { background-color: #F3F4F6; }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        .exec-header {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            padding: 30px 40px; border-radius: 16px; border-left: 8px solid #D4AF37;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 30px; margin-top: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .exec-title h1 { color: #FFFFFF !important; font-size: 32px; font-weight: 800; margin: 0; letter-spacing: -0.5px;}
        .exec-title p { color: #94A3B8 !important; font-size: 15px; margin: 8px 0 0 0; font-weight: 500; }
        
        .kpi-wrapper { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .kpi-card {
            flex: 1; min-width: 230px; background: #FFFFFF; padding: 25px; border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #E2E8F0;
        }
        .kpi-title { color: #64748B; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
        .kpi-value { color: #0F172A; font-size: 36px; font-weight: 800; margin-top: 10px; }
        .val-siap { color: #059669; }
        .val-proses { color: #D97706; }

        .filter-bar {
            background: white; padding: 20px 25px 20px 25px; border-radius: 12px;
            border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 20px;
        }

        .proj-card {
            background: white; border-radius: 12px; padding: 25px;
            border: 1px solid #E2E8F0; border-top: 5px solid #1E293B; margin-top: 10px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        .proj-title { color: #0F172A; font-size: 22px; font-weight: 700; margin-bottom: 5px; }
        .proj-agency { color: #64748B; font-size: 15px; font-weight: 500; margin-bottom: 15px;}
        
        .badge { padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; display: inline-block; }
        .b-siap { background: #D1FAE5; color: #065F46; border: 1px solid #34D399; }
        .b-proses { background: #FEF3C7; color: #92400E; border: 1px solid #FBBF24; }
        .b-lewat { background: #FEE2E2; color: #991B1B; border: 1px solid #F87171; }
        hr { border-color: #E2E8F0; margin: 15px 0; }
        
        /* Ubah design butang expander supaya nampak macam landing page button */
        .streamlit-expanderHeader {
            font-size: 16px !important;
            font-weight: bold !important;
            color: #1E293B !important;
            background-color: #F8FAFC !important;
            border-radius: 8px !important;
            border: 1px solid #E2E8F0 !important;
        }
    </style>
""", unsafe_allow_html=True)

def get_base64_image(file_name):
    for ext in ['.png', '.jpg', '.jpeg']:
        path = f"{file_name}{ext}"
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f"data:image/{ext.replace('.', '')};base64,{base64.b64encode(f.read()).decode()}"
    return None

# FUNGSI BARU: Cari BANYAK link gambar serentak dari satu petak
def dapatkan_senarai_gambar(teks):
    if pd.isna(teks) or teks == "-": return []
    teks = str(teks)
    
    # Cari semua ID Google drive yang dicampur-campur
    ids = re.findall(r'/d/([a-zA-Z0-9_-]+)', teks)
    ids += re.findall(r'id=([a-zA-Z0-9_-]+)', teks)
    
    # Buang ID yang berulang (duplicate)
    ids = list(set(ids))
    
    urls = []
    for file_id in ids:
        urls.append(f"https://drive.google.com/uc?export=view&id={file_id}")
    return urls

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

# ==========================================
# 1. LOGO JATA & JABATAN
# ==========================================
jata_img = get_base64_image("jata")
jabatan_img = get_base64_image("jabatan")

logo_html = '<div style="display: flex; align-items: center; gap: 25px; margin-bottom: 5px;">'
if jata_img:
    logo_html += f'<img src="{jata_img}" style="height: 90px; object-fit: contain;">'
if jabatan_img:
    logo_html += f'<img src="{jabatan_img}" style="height: 90px; object-fit: contain;">'
logo_html += '</div>'

st.markdown(logo_html, unsafe_allow_html=True)

with st.spinner('Menyegerak pangkalan data MOTAC...'):
    df = load_data(SHEET_URL)

if not df.empty:
    
    tarikh_last_save = "Tiada Rekod"
    if 'Tarikh Kemaskini' in df.columns:
        tarikh_sah = df[df['Tarikh Kemaskini'] != '-']['Tarikh Kemaskini']
        if not tarikh_sah.empty:
            tarikh_last_save = tarikh_sah.iloc[0]

    # ==========================================
    # 2. BANNER UTAMA
    # ==========================================
    st.markdown(f"""
        <div class="exec-header">
            <div class="exec-title">
                <h1>DASHBOARD EKSEKUTIF PPUN</h1>
                <p>Pemantauan Projek Infrastruktur Pelancongan | <b>Dikemaskini: {tarikh_last_save} (Berdasarkan Rekod Sheet)</b></p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 3. KAD KPI STATISTIK
    # ==========================================
    jumlah_projek = len(df)
    siap = df[df['Status Semasa'].astype(str).str.contains("Siap|Selesai", case=False, na=False)].shape[0] if 'Status Semasa' in df.columns else 0
    proses = df[df['Status Semasa'].astype(str).str.contains("Proses|Progress|Laksana|Sedang", case=False, na=False)].shape[0] if 'Status Semasa' in df.columns else 0

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

    # ==========================================
    # 4. PANEL KAWALAN & DROPDOWN PROJEK
    # ==========================================
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color:#0F172A; font-size:16px;'>⚙️ Panel Carian & Pemilihan Projek</h4>", unsafe_allow_html=True)
    
    senarai_agensi = ["Semua Agensi"] + list(df['Agensi Pelaksana'].unique()) if 'Agensi Pelaksana' in df.columns else ["Semua Agensi"]
    senarai_agensi = [x for x in senarai_agensi if x != "-"]
    
    col_f1, col_f2, col_f3, col_f4 = st.columns([2.5, 2, 2, 1.5])
    with col_f1: carian_teks = st.text_input("🔍 Cari Projek / Kontraktor:")
    with col_f2: pilih_agensi = st.selectbox("🏢 Agensi Pelaksana:", senarai_agensi)
    with col_f3: pilih_status = st.selectbox("📊 Status:", ["Semua Status", "Telah Siap", "Dalam Pelaksanaan", "Lain-lain"])
    with col_f4: 
        st.write("")
        if st.button("🔄 *Refresh*", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    df_tapis = df.copy()
    if carian_teks:
        mask = pd.Series([False] * len(df_tapis))
        for col in df_tapis.columns: mask = mask | df_tapis[col].astype(str).str.contains(carian_teks, case=False, na=False)
        df_tapis = df_tapis[mask]
    if pilih_agensi != "Semua Agensi": df_tapis = df_tapis[df_tapis['Agensi Pelaksana'] == pilih_agensi]
    if pilih_status != "Semua Status":
        if pilih_status == "Telah Siap": df_tapis = df_tapis[df_tapis['Status Semasa'].astype(str).str.contains("Siap|Selesai", case=False, na=False)]
        elif pilih_status == "Dalam Pelaksanaan": df_tapis = df_tapis[df_tapis['Status Semasa'].astype(str).str.contains("Proses|Progress|Laksana|Sedang", case=False, na=False)]

    st.write("---")
    senarai_projek = ["-- Sila Pilih Projek Untuk Dipaparkan --"] + df_tapis['Tajuk Program'].tolist()
    pilihan_akhir = st.selectbox("🎯 Pilih Projek:", senarai_projek)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 5. KAD PROJEK & GALERI GAMBAR
    # ==========================================
    if pilihan_akhir != "-- Sila Pilih Projek Untuk Dipaparkan --":
        
        row = df_tapis[df_tapis['Tajuk Program'] == pilihan_akhir].iloc[0]
        
        stat_text = str(row.get('Status Semasa', '-'))
        if "siap" in stat_text.lower() or "selesai" in stat_text.lower(): badge_html = f"<span class='badge b-siap'>✓ {stat_text.upper()}</span>"
        elif "proses" in stat_text.lower() or "laksana" in stat_text.lower() or "sedang" in stat_text.lower(): badge_html = f"<span class='badge b-proses'>⏳ {stat_text.upper()}</span>"
        else: badge_html = f"<span class='badge b-lewat'>⚠️ {stat_text.upper()}</span>"

        # Dapatkan Tarikh Kemaskini Khusus Projek Ini
        tarikh_projek_ini = row.get('Tarikh Kemaskini', 'Tiada Tarikh')

        with st.container():
            st.markdown(f"""
            <div class="proj-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div class="proj-title">#{row.get('Bil.', '-')} {row.get('Tajuk Program', '-')}</div>
                        <div class="proj-agency">🏢 {row.get('Agensi Pelaksana', '-')}</div>
                    </div>
                    <div style="text-align: right;">{badge_html}</div>
                </div>
                <hr>
            """, unsafe_allow_html=True)
            
            # Maklumat Projek
            col1, col2, col3 = st.columns([1.5, 1, 1])
            with col1:
                st.markdown("**📌 Skop Kerja Utama:**")
                st.info(row.get('Skop Kerja', '-'))
            with col2:
                st.markdown("**💰 Kewangan & Tempoh:**")
                st.write(f"**Peruntukan:** {row.get('Peruntukkan', '-')}")
                st.write(f"**Kos Projek:** {row.get('Kos Projek', '-')}")
                st.write(f"**Tarikh Mula:** {row.get('Tarikh Mula', '-')}")
                st.write(f"**Tarikh Siap:** {row.get('Tarikh Siap', '-')}")
            with col3:
                st.markdown("**👷🏻‍♂️ Pelaksanaan:**")
                st.write(f"**Kontraktor:** {row.get('Kontraktor', '-')}")
                st.write(f"**Kemajuan Fizikal:** {row.get('Peratus Siap Kerja', '-')}")
                st.write(f"**Tarikh Kemaskini:** {tarikh_projek_ini}")
            
            st.markdown("<hr style='border-color: #E2E8F0;'>", unsafe_allow_html=True)
            
            # RUANG LANDING PAGE GAMBAR (GALERI)
            senarai_gambar = dapatkan_senarai_gambar(row.get('Gambar Projek', '-'))
            
            if senarai_gambar:
                with st.expander("📸 KLIK DI SINI UNTUK BUKA GALERI GAMBAR PROJEK"):
                    st.markdown(f"<h4 style='color:#1E293B; text-align:center;'>Visual Tapak Projek (Kemaskini: {tarikh_projek_ini})</h4><br>", unsafe_allow_html=True)
                    
                    # Susun gambar dalam grid 3 lajur supaya kemas walau banyak gambar
                    img_cols = st.columns(3)
                    for i, img_url in enumerate(senarai_gambar):
                        with img_cols[i % 3]:
                            st.image(img_url, caption=f"Gambar {i+1} | Tarikh: {tarikh_projek_ini}", use_container_width=True)
            else:
                st.info("📷 Tiada gambar dimasukkan untuk projek ini.")
                
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("👆 Sila gunakan kotak 'Pilih Projek' di atas untuk memaparkan butiran dan gambar.")

    # ==========================================
    # 6. LOGO MADANI (TENGAH BAWAH)
    # ==========================================
    st.write("")
    st.write("")
    madani_img = get_base64_image("madani")
    if madani_img:
        st.markdown(f"""
            <div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
                <img src="{madani_img}" style="height: 120px; object-fit: contain;">
            </div>
        """, unsafe_allow_html=True)

else:
    st.error("Gagal menarik data. Pastikan Google Sheet diset kepada 'Anyone with the link' (Viewer).")
