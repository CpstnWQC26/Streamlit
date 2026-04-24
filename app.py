import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Aqua Monitoring Dashboard", page_icon="🌊", layout="wide")
sns.set_theme(style="whitegrid")

# 2. JUDUL DAN PENGANTAR
st.title("🌊 Aqua Monitoring: Monitoring Kualitas Air")
st.markdown("""
Sistem ini menyajikan analisis mendalam dari data perairan untuk mendeteksi potensi krisis ekologis secara proaktif.
""")

# 3. MEMUAT DATA
@st.cache_data
def load_data():
    # Menggunakan dataset yang sudah dibersihkan sebelumnya
    df = pd.read_csv("water_quality_ready.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)
    return df

df = load_data()

# 4. TAMPILAN DATA MENTAH (10 TERATAS)
if st.checkbox("Tampilkan 5 Data Teratas"):
    st.subheader("Cuplikan Dataset Bersih")
    st.dataframe(df.head(15)) # 10 baris pertama

st.divider()

# =========================================================
# ANALISIS BERDASARKAN 4 PERTANYAAN & INSIGHT UTAMA
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Korelasi Parameter", 
    "🌊 Arus & Kekeruhan (Q1)", 
    "🌡️ Suhu & Oksigen (Q2)", 
    "⚠️ Deteksi Anomali (Q3)"
])

# --- TAB 1: KORELASI ANTAR PARAMETER (EDA INSIGHT) ---
with tab1:
    st.header("Analisis Hubungan Antar Seluruh Parameter")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    # Visualisasi heatmap korelasi dari EDA
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax1)
    st.pyplot(fig1)
    st.info("**Insight:** Parameter seperti Salinitas dan Konduktivitas memiliki korelasi yang sangat tinggi (mendekati 1), sedangkan Oksigen Terlarut menunjukkan hubungan negatif yang kuat dengan Suhu.")

# --- TAB 2: PENGARUH ARUS TERHADAP KEKERUHAN (Q1) ---
with tab2:
    st.header("Bagaimana pengaruh kecepatan arus terhadap tingkat kekeruhan air?")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    # Scatter plot Arus vs Kekeruhan
    sns.scatterplot(data=df, x='Average Water Speed', y='Turbidity', alpha=0.4, color='teal', ax=ax2)
    ax2.set_title('Kecepatan Arus vs Turbidity', fontweight='bold')
    st.pyplot(fig2)
    st.info("**Insight:** Grafik ini membantu memantau apakah peningkatan kecepatan arus secara langsung memicu kenaikan sedimen atau kekeruhan di lokasi pemantauan.")

# --- TAB 3: DAMPAK SUHU TERHADAP OKSIGEN (Q2) ---
with tab3:
    st.header("Seberapa besar dampak kenaikan suhu terhadap kadar oksigen?")
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Regplot Suhu vs DO
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.regplot(data=df, x='Temperature', y='Dissolved Oxygen', 
                    scatter_kws={'alpha':0.2, 'color':'teal'}, 
                    line_kws={'color':'red', 'linewidth':3}, ax=ax3)
        st.pyplot(fig3)
        
    with col_b:
        # Tren harian Suhu & DO
        df_harian = df.resample('D').mean()
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        ax4.plot(df_harian.index, df_harian['Temperature'], color='tab:red', label='Suhu')
        ax5 = ax4.twinx()
        ax5.plot(df_harian.index, df_harian['Dissolved Oxygen'], color='tab:blue', label='Oksigen')
        st.pyplot(fig4)
        
    st.info("**Insight:** Terlihat pola 'efek cermin'; saat suhu meningkat, kadar oksigen terlarut cenderung menurun secara signifikan, yang dapat mengancam ekosistem.")

# --- TAB 4: DETEKSI ANOMALI TEMPORAL (Q3) ---
with tab4:
    st.header("Pola Waktu Terjadinya Lonjakan Kekeruhan yang Tidak Wajar")
    fig5, ax6 = plt.subplots(figsize=(12, 6))
    # Line chart dengan penanda anomali/outlier
    plt.plot(df.index, df['Turbidity'], color='gray', label='Normal', alpha=0.5)
    batas_ekstrem = df['Turbidity'].quantile(0.99)
    outliers = df[df['Turbidity'] > batas_ekstrem]
    plt.scatter(outliers.index, outliers['Turbidity'], color='red', label='Anomali (Extreme)', zorder=5)
    plt.legend()
    st.pyplot(fig5)
    st.info("**Insight:** Titik-titik merah mengidentifikasi waktu spesifik terjadinya anomali kekeruhan tinggi yang memerlukan perhatian lebih lanjut.")

# --- TAB 5: PERBANDINGAN BATAS AMAN (Q4) ---
with tab5:
    st.header("Kondisi Kualitas Air Dibandingkan Batas Aman")
    st.markdown("Analisis ini membandingkan data aktual dengan standar kualitas air (Batas Aman).")
    
    # Menentukan Ambang Batas (Thresholds)
    limits = {
        'pH': (6.5, 8.5),
        'Dissolved Oxygen': 4.0, # Minimal 4 mg/L
        'Temperature': 32.0,      # Maksimal 32 C
        'Turbidity': 50.0         # Maksimal 50 FNU
    }
    
    # Menghitung Persentase Kepatuhan
    status = {
        'pH': ((df['pH'] >= limits['pH'][0]) & (df['pH'] <= limits['pH'][1])).mean() * 100,
        'Oksigen (DO)': (df['Dissolved Oxygen'] >= limits['Dissolved Oxygen']).mean() * 100,
        'Suhu': (df['Temperature'] <= limits['Temperature']).mean() * 100,
        'Kekeruhan': (df['Turbidity'] <= limits['Turbidity']).mean() * 100
    }
    
    # Visualisasi dengan Bar Chart
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    colors = ['green' if v > 80 else 'orange' for v in status.values()]
    sns.barplot(x=list(status.keys()), y=list(status.values()), palette=colors, ax=ax5)
    ax5.axhline(100, color='black', linestyle='--')
    ax5.set_ylabel("Persentase Data Aman (%)")
    ax5.set_ylim(0, 110)
    st.pyplot(fig5)
    
    st.info(f"""
    **Insight Pertanyaan 4:** - **pH**: {status['pH']:.1f}% data berada dalam rentang aman (6.5 - 8.5).
    - **Oksigen**: {status['Oksigen (DO)']:.1f}% data memenuhi syarat minimal 4 mg/L.
    - **Suhu**: {status['Suhu']:.1f}% data berada di bawah batas maksimal 32°C.
    - **Kekeruhan**: {status['Kekeruhan']:.1f}% data berada di bawah batas maksimal 50 FNU.
    """)
