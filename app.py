import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. PENGATURAN HALAMAN WEB
st.set_page_config(page_title="Aqua Monitoring Dashboard", page_icon="🌊", layout="wide")
sns.set_theme(style="whitegrid")

# 2. JUDUL DAN DESKRIPSI
st.title("🌊 Aqua Monitoring: Sistem Peringatan Dini Kualitas Air Estuari")
st.markdown("""
Selamat datang di dasbor **Aqua Monitoring**. Dasbor ini menyajikan hasil analisis data historis perairan 
untuk memantau parameter fisik dan kimia air, serta mendeteksi potensi anomali yang dapat memicu krisis ekologis.
""")

# 3. MENGAMBIL DATA BERSIH 
@st.cache_data
def load_data():
    # File CSV
    df = pd.read_csv("water_quality_ready.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)
    return df

df = load_data()

# 4. TAMPILAN SEKILAS DATA
if st.checkbox("Tampilkan Data Mentah"):
    st.subheader("Data Kualitas Air (Sudah Dibersihkan)")
    st.dataframe(df.tail())

st.divider()

# =========================================================
# VISUALISASI MENGGUNAKAN TAB
# =========================================================
tab1, tab2 = st.tabs(["📊 Analisis Suhu & Oksigen (Q2)", "🌊 Analisis Arus & Kekeruhan (Q1)"])

with tab1:
    st.header("Seberapa besar dampak kenaikan suhu air terhadap penurunan kadar oksigen?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Grafik Regresi
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        sns.regplot(data=df, x='Temperature', y='Dissolved Oxygen', 
                    scatter_kws={'alpha':0.2, 'color':'teal'}, 
                    line_kws={'color':'red', 'linewidth':3}, ax=ax1)
        ax1.set_title('Korelasi Suhu vs Oksigen Terlarut', fontweight='bold')
        ax1.set_xlabel('Suhu Air (°C)')
        ax1.set_ylabel('Oksigen Terlarut (mg/L)')
        st.pyplot(fig1)
        
    with col2:
        # Grafik Tren Harian
        df_harian = df.resample('D').mean()
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        warna_suhu = 'tab:red'
        ax2.set_xlabel('Waktu')
        ax2.set_ylabel('Suhu Air (°C)', color=warna_suhu)
        ax2.plot(df_harian.index, df_harian['Temperature'], color=warna_suhu, linewidth=2, label='Suhu')
        ax2.tick_params(axis='y', labelcolor=warna_suhu)

        ax3 = ax2.twinx()  
        warna_oksigen = 'tab:blue'
        ax3.set_ylabel('Oksigen (mg/L)', color=warna_oksigen)
        ax3.plot(df_harian.index, df_harian['Dissolved Oxygen'], color=warna_oksigen, linewidth=2, label='Oksigen')
        ax3.tick_params(axis='y', labelcolor=warna_oksigen)
        
        plt.title('Pola Rata-rata Harian Suhu vs Oksigen', fontweight='bold')
        st.pyplot(fig2)
        
    st.info("**Insight:** Garis merah yang menukik tajam pada grafik pertama dan pola cermin pada grafik kedua membuktikan bahwa semakin panas air, kadar oksigennya semakin menipis. Ini adalah indikator penting untuk mencegah ikan mati.")

with tab2:
    st.header("Bagaimana pengaruh kecepatan arus terhadap tingkat kekeruhan air?")
    
    fig3, ax4 = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df, x='Average Water Speed', y='Turbidity', alpha=0.4, color='teal', ax=ax4)
    ax4.set_title('Kecepatan Arus vs Kekeruhan (Turbidity)', fontweight='bold')
    ax4.set_xlabel('Kecepatan Arus Air (cm/s)')
    ax4.set_ylabel('Kekeruhan (FNU)')
    st.pyplot(fig3)
    
    st.info("**Insight:** Melalui sebaran titik ini, kita dapat memantau apakah sedimen tanah lebih banyak terangkat (air keruh) ketika arus sedang mengalir deras.")
