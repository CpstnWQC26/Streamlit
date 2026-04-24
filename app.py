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

# 4. TAMPILAN DATA MENTAH (15 TERATAS)
if st.checkbox("Tampilkan 15 Data Teratas"):
    st.subheader("Cuplikan Dataset Bersih")
    st.dataframe(df.head(15)) # 15 baris pertama

st.divider()

# =========================================================
# ANALISIS BERDASARKAN 4 PERTANYAAN & INSIGHT UTAMA
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 Korelasi Parameter", 
    "🌊 Arus & Kekeruhan (Q1)", 
    "🌡️ Suhu & Oksigen (Q2)", 
    "⚠️ Deteksi Anomali (Q3)",
    "✅ Batas Aman (Q4)"
])

# --- TAB 1: KORELASI ANTAR PARAMETER (EDA INSIGHT) ---
with tab1:
    st.header("Analisis Hubungan Antar Seluruh Parameter")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    # Visualisasi heatmap korelasi dari EDA
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax1)
    st.pyplot(fig1)
    st.info("**Insight:** Parameter seperti Salinitas dan Konduktivitas memiliki korelasi yang sangat tinggi (mendekati 1), sedangkan Oksigen Terlarut menunjukkan hubungan negatif yang kuat dengan Suhu. Dari heatmap korelasi terlihat bahwa terdapat beberapa hubungan kuat antar parameter kualitas air. Dissolved Oxygen memiliki korelasi negatif cukup kuat dengan Temperature (sekitar -0.63), yang menunjukkan bahwa semakin tinggi suhu air, kadar oksigen terlarut cenderung menurun. Selain itu, Salinity dan Specific Conductance memiliki korelasi yang sangat tinggi (mendekati 1), menandakan keduanya hampir merepresentasikan hal yang sama sehingga berpotensi redundan. Dissolved Oxygen juga memiliki korelasi positif kuat dengan Dissolved Oxygen (%Saturation) dan cukup tinggi dengan pH, yang menunjukkan keterkaitan antar parameter kimia air. Sementara itu, variabel seperti Chlorophyll dan Turbidity cenderung memiliki korelasi lemah terhadap parameter lain, menandakan pengaruhnya lebih independen. Secara keseluruhan, pola ini menunjukkan bahwa parameter fisik seperti suhu memiliki pengaruh signifikan terhadap kondisi kimia air, sementara beberapa variabel lain bergerak lebih bebas tanpa hubungan yang kuat.")

# --- TAB 2: PENGARUH ARUS TERHADAP KEKERUHAN (Q1) ---
with tab2:
    st.header("Bagaimana pengaruh kecepatan arus terhadap tingkat kekeruhan air?")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    # Scatter plot Arus vs Kekeruhan
    sns.scatterplot(data=df, x='Average Water Speed', y='Turbidity', alpha=0.4, color='teal', ax=ax2)
    ax2.set_title('Kecepatan Arus vs Turbidity', fontweight='bold')
    st.pyplot(fig2)
    st.info("**Insight:** Grafik ini membantu memantau apakah peningkatan kecepatan arus secara langsung memicu kenaikan sedimen atau kekeruhan di lokasi pemantauan. Dari visualisasi hubungan antara kecepatan arus dan tingkat kekeruhan air (turbidity), terlihat bahwa tidak terdapat hubungan linear yang kuat antara kedua variabel tersebut, yang ditunjukkan oleh sebaran data yang sangat luas dan tidak membentuk pola tertentu. Meskipun garis tren menunjukkan kecenderungan sedikit meningkat (positif), hal ini sangat lemah dan tidak signifikan secara visual. Selain itu, terdapat banyak nilai turbidity tinggi yang tersebar pada berbagai tingkat kecepatan arus, yang menunjukkan bahwa kekeruhan air tidak hanya dipengaruhi oleh kecepatan arus, tetapi kemungkinan besar juga dipengaruhi oleh faktor lain seperti aktivitas sedimen, curah hujan, atau kondisi lingkungan sekitar. Dengan demikian, kecepatan arus bukan merupakan indikator utama dalam menentukan tingkat kekeruhan air pada dataset ini.")

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
        
    st.info("**Insight:** Garis merah pada grafik 1 yang menukik tajam ke bawah membuktikan bahwa semakin panas air, kadar oksigennya semakin menipis. Ini adalah indikator krisis ekologis yang penting. Pada grafik 2 terlihat pola 'efek cermin'; saat suhu meningkat, kadar oksigen terlarut cenderung menurun secara signifikan, yang dapat mengancam ekosistem.")

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
with tab5:params = ['Temperature', 'Dissolved Oxygen', 'pH', 'Turbidity']

thresholds = {}

for col in params:
    if col == 'Dissolved Oxygen':
        thresholds[col] = {
            'warning': df[col].quantile(0.10),
            'critical': df[col].quantile(0.05)
        }
    else:
        thresholds[col] = {
            'warning': df[col].quantile(0.90),
            'critical': df[col].quantile(0.95)
        }

def classify(val, col):
    if col == 'Dissolved Oxygen':
        if val < thresholds[col]['critical']:
            return 'critical'
        elif val < thresholds[col]['warning']:
            return 'warning'
        else:
            return 'normal'
    else:
        if val > thresholds[col]['critical']:
            return 'critical'
        elif val > thresholds[col]['warning']:
            return 'warning'
        else:
            return 'normal'

for col in params:
    df[col + '_level'] = df[col].apply(lambda x: classify(x, col))

level_cols = [col + '_level' for col in params]

def overall_status(row):
    if 'critical' in row.values:
        return 'critical'
    elif 'warning' in row.values:
        return 'warning'
    else:
        return 'normal'

df['overall_status'] = df[level_cols].apply(overall_status, axis=1)

overall_pct = df['overall_status'].value_counts(normalize=True) * 100
print("Persentase Kondisi Air:")
print(overall_pct)

import matplotlib.pyplot as plt

monthly_dist = (
    df.groupby('month')['overall_status']
    .value_counts(normalize=True)
    .unstack()
    * 100
)

monthly_dist.plot(
    kind='bar',
    stacked=True,
    figsize=(12,6),
    title='Distribusi Kondisi Kualitas Air per Bulan (%)'
)

plt.ylabel('Persentase (%)')
plt.show()

st.info("**Insight:** Berdasarkan distribusi kondisi kualitas air per bulan, terlihat bahwa kategori normal mendominasi pada sebagian besar periode, terutama pada bulan ke-3, ke-8, dan ke-9 yang menunjukkan kondisi relatif stabil. Namun, terdapat peningkatan signifikan pada kondisi critical dan warning di bulan ke-2, ke-6, ke-7, ke-11, dan ke-12, yang menunjukkan adanya penurunan kualitas air pada periode tersebut. Khususnya, bulan ke-2 dan ke-12 memiliki proporsi kondisi critical yang cukup tinggi dibanding bulan lainnya, mengindikasikan potensi kejadian pencemaran atau kondisi ekstrem yang lebih sering terjadi. Pola ini menunjukkan adanya kecenderungan musiman dalam kualitas air, di mana beberapa bulan tertentu lebih rentan terhadap kondisi tidak normal sehingga memerlukan perhatian dan pemantauan yang lebih intensif.")
