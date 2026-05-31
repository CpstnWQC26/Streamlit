
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Insight & Kesimpulan Kualitas Air",
    page_icon="💧",
    layout="wide"
)

# ============================================================
# KONFIGURASI FILE DATASET
# ============================================================

DATA_PATH = Path("dataset.csv")

# ============================================================
# FUNCTION
# ============================================================

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        st.error(
            "File dataset.csv tidak ditemukan. "
            "Letakkan file dataset dengan nama dataset.csv di folder yang sama dengan app ini."
        )
        st.stop()

    return pd.read_csv(DATA_PATH, low_memory=False)

def preprocess_data(df):
    df = df.copy()

    if "Timestamp" in df.columns:
        df = df[df["Timestamp"] != "Units"].copy()
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    drop_cols = ["_id", "Record number", "quality"]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors="ignore")

    numeric_cols = [
        "Average Water Speed",
        "Average Water Direction",
        "Chlorophyll",
        "Temperature",
        "Dissolved Oxygen",
        "Dissolved Oxygen (%Saturation)",
        "pH",
        "Salinity",
        "Specific Conductance",
        "Turbidity"
    ]

    numeric_cols = [col for col in numeric_cols if col in df.columns]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Timestamp" in df.columns:
        df = df.sort_values("Timestamp").reset_index(drop=True)

    for col in numeric_cols:
        df[col] = df[col].interpolate(method="linear", limit_direction="both")
        df[col] = df[col].fillna(df[col].median())

    df_capped = df.copy()

    for col in numeric_cols:
        lower = df_capped[col].quantile(0.01)
        upper = df_capped[col].quantile(0.99)
        df_capped[col] = df_capped[col].clip(lower=lower, upper=upper)

    if "Timestamp" in df_capped.columns:
        df_capped["hour"] = df_capped["Timestamp"].dt.hour
        df_capped["date"] = df_capped["Timestamp"].dt.date
        df_capped["month"] = df_capped["Timestamp"].dt.month

    return df_capped, numeric_cols

def create_status(df):
    df = df.copy()

    params = ["Temperature", "Dissolved Oxygen", "pH", "Turbidity"]
    params = [col for col in params if col in df.columns]

    thresholds = {}

    for col in params:
        if col == "Dissolved Oxygen":
            thresholds[col] = {
                "warning": df[col].quantile(0.10),
                "critical": df[col].quantile(0.05)
            }
        else:
            thresholds[col] = {
                "warning": df[col].quantile(0.90),
                "critical": df[col].quantile(0.95)
            }

    def classify(val, col):
        if col == "Dissolved Oxygen":
            if val < thresholds[col]["critical"]:
                return "critical"
            elif val < thresholds[col]["warning"]:
                return "warning"
            else:
                return "normal"
        else:
            if val > thresholds[col]["critical"]:
                return "critical"
            elif val > thresholds[col]["warning"]:
                return "warning"
            else:
                return "normal"

    level_cols = []

    for col in params:
        level_col = col + "_level"
        df[level_col] = df[col].apply(lambda x: classify(x, col))
        level_cols.append(level_col)

    def overall_status(row):
        if "critical" in row.values:
            return "critical"
        elif "warning" in row.values:
            return "warning"
        else:
            return "normal"

    df["overall_status"] = df[level_cols].apply(overall_status, axis=1)

    return df, thresholds, level_cols

def detect_anomaly(df):
    df = df.copy()

    if "Turbidity" not in df.columns:
        return df, None

    q1 = df["Turbidity"].quantile(0.25)
    q3 = df["Turbidity"].quantile(0.75)
    iqr = q3 - q1
    upper_limit = q3 + 1.5 * iqr

    df["turbidity_anomaly"] = df["Turbidity"] > upper_limit

    return df, upper_limit

# ============================================================
# MAIN
# ============================================================

st.title("Dashboard Insight dan Kesimpulan Kualitas Air")

st.markdown(
    """
Mohon tunggu sebentar, dashboard sedang memproses data dan menghasilkan insight utama berdasarkan dataset kualitas air yang telah disediakan.
"""
)

df_raw = load_data()
df, numeric_cols = preprocess_data(df_raw)
df, thresholds, level_cols = create_status(df)
df, turbidity_upper_limit = detect_anomaly(df)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💧 Insight Dashboard")
st.sidebar.success("Dataset berhasil dibaca dari dataset.csv")

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
**Ukuran dataset:**

- Baris: `{df.shape[0]:,}`
- Kolom: `{df.shape[1]:,}`
"""
)

# ============================================================
# KPI
# ============================================================

st.header("Ringkasan Utama")

total_data = len(df)
normal_count = int((df["overall_status"] == "normal").sum())
warning_count = int((df["overall_status"] == "warning").sum())
critical_count = int((df["overall_status"] == "critical").sum())
anomaly_count = int(df["turbidity_anomaly"].sum()) if "turbidity_anomaly" in df.columns else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Data", f"{total_data:,}")
col2.metric("Normal", f"{normal_count:,}")
col3.metric("Warning", f"{warning_count:,}")
col4.metric("Critical", f"{critical_count:,}")

col5, col6 = st.columns(2)
col5.metric("Anomali Turbidity", f"{anomaly_count:,}")
col6.metric("Persentase Anomali", f"{(anomaly_count / total_data * 100):.2f}%")

# ============================================================
# INSIGHT 1
# ============================================================

st.header("Insight 1: Kondisi Umum Kualitas Air")

status_count = (
    df["overall_status"]
    .value_counts()
    .reindex(["normal", "warning", "critical"])
    .fillna(0)
    .reset_index()
)

status_count.columns = ["Status", "Jumlah"]

fig_status = px.bar(
    status_count,
    x="Status",
    y="Jumlah",
    color="Status",
    title="Distribusi Status Kualitas Air",
    text="Jumlah"
)

st.plotly_chart(fig_status, use_container_width=True)

dominant_status = status_count.sort_values("Jumlah", ascending=False).iloc[0]["Status"]

st.markdown(
    f"""
**Insight:** Status kualitas air yang paling dominan adalah **{dominant_status}**.
Hal ini menunjukkan bahwa mayoritas kondisi air dalam dataset berada pada kategori tersebut.
"""
)

# ============================================================
# INSIGHT 2
# ============================================================

st.header("Insight 2: Pengaruh Kecepatan Arus terhadap Kekeruhan Air")

if "Average Water Speed" in df.columns and "Turbidity" in df.columns:
    corr_speed_turbidity = df["Average Water Speed"].corr(df["Turbidity"])

    fig_speed = px.scatter(
        df,
        x="Average Water Speed",
        y="Turbidity",
        trendline="ols",
        title=f"Hubungan Kecepatan Arus dengan Turbidity | Korelasi: {corr_speed_turbidity:.3f}"
    )

    st.plotly_chart(fig_speed, use_container_width=True)

    if corr_speed_turbidity > 0.5:
        speed_insight = "hubungan positif kuat"
    elif corr_speed_turbidity > 0.2:
        speed_insight = "hubungan positif lemah hingga sedang"
    elif corr_speed_turbidity < -0.2:
        speed_insight = "hubungan negatif"
    else:
        speed_insight = "hubungan linear yang sangat lemah"

    st.markdown(
        f"""
**Insight:** Korelasi antara kecepatan arus dan turbidity adalah **{corr_speed_turbidity:.3f}**,
yang menunjukkan **{speed_insight}**. Artinya, kecepatan arus belum tentu menjadi faktor utama
yang memengaruhi kekeruhan air secara langsung.
"""
    )

# ============================================================
# INSIGHT 3
# ============================================================

st.header("Insight 3: Dampak Suhu terhadap Dissolved Oxygen")

if "Temperature" in df.columns and "Dissolved Oxygen" in df.columns:
    corr_temp_do = df["Temperature"].corr(df["Dissolved Oxygen"])

    fig_temp_do = px.scatter(
        df,
        x="Temperature",
        y="Dissolved Oxygen",
        trendline="ols",
        title=f"Hubungan Temperature dengan Dissolved Oxygen | Korelasi: {corr_temp_do:.3f}"
    )

    st.plotly_chart(fig_temp_do, use_container_width=True)

    if corr_temp_do < -0.5:
        temp_insight = "kenaikan suhu berkaitan kuat dengan penurunan kadar oksigen"
    elif corr_temp_do < -0.2:
        temp_insight = "kenaikan suhu cenderung berkaitan dengan penurunan kadar oksigen"
    elif corr_temp_do > 0.2:
        temp_insight = "kenaikan suhu cenderung berkaitan dengan kenaikan kadar oksigen"
    else:
        temp_insight = "hubungan antara suhu dan dissolved oxygen relatif lemah"

    st.markdown(
        f"""
**Insight:** Korelasi antara Temperature dan Dissolved Oxygen adalah **{corr_temp_do:.3f}**.
Berdasarkan nilai tersebut, **{temp_insight}**.
"""
    )

# ============================================================
# INSIGHT 4
# ============================================================

st.header("Insight 4: Pola Waktu Anomali Turbidity")

if "hour" in df.columns and "turbidity_anomaly" in df.columns:
    hourly_anomaly = (
        df.groupby("hour")["turbidity_anomaly"]
        .agg(anomaly_count="sum", total_data="count", anomaly_rate="mean")
        .reset_index()
    )

    hourly_anomaly["anomaly_rate_percent"] = hourly_anomaly["anomaly_rate"] * 100

    fig_hour_anomaly = px.line(
        hourly_anomaly,
        x="hour",
        y="anomaly_count",
        markers=True,
        title="Jumlah Anomali Turbidity Berdasarkan Jam"
    )

    st.plotly_chart(fig_hour_anomaly, use_container_width=True)

    top_hour = hourly_anomaly.sort_values("anomaly_count", ascending=False).iloc[0]

    st.markdown(
        f"""
**Insight:** Anomali turbidity paling banyak terjadi pada jam **{int(top_hour['hour'])}**,
dengan jumlah anomali sebanyak **{int(top_hour['anomaly_count'])}** data.
"""
    )

# ============================================================
# INSIGHT 5
# ============================================================

st.header("Insight 5: Parameter yang Paling Sering Memicu Warning")

warning_summary = {}

for col in ["Temperature", "Dissolved Oxygen", "pH", "Turbidity"]:
    level_col = col + "_level"
    if level_col in df.columns:
        warning_summary[col] = int((df[level_col] == "warning").sum())

warning_df = (
    pd.DataFrame({
        "Parameter": list(warning_summary.keys()),
        "Jumlah Warning": list(warning_summary.values())
    })
    .sort_values("Jumlah Warning", ascending=False)
)

fig_warning = px.bar(
    warning_df,
    x="Jumlah Warning",
    y="Parameter",
    orientation="h",
    title="Jumlah Warning Berdasarkan Parameter"
)

fig_warning.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_warning, use_container_width=True)

top_warning_param = warning_df.iloc[0]["Parameter"] if len(warning_df) > 0 else "-"

st.markdown(
    f"""
**Insight:** Parameter yang paling sering memicu status warning adalah **{top_warning_param}**.
Parameter ini perlu menjadi perhatian utama dalam sistem pemantauan kualitas air.
"""
)

# ============================================================
# INSIGHT 6
# ============================================================

st.header("Insight 6: Tren Kondisi Kualitas Air Harian")

if "date" in df.columns:
    daily_status = (
        df.groupby(["date", "overall_status"])
        .size()
        .reset_index(name="count")
    )

    daily_total = (
        df.groupby("date")
        .size()
        .reset_index(name="total")
    )

    daily_status = daily_status.merge(daily_total, on="date")
    daily_status["percentage"] = daily_status["count"] / daily_status["total"] * 100

    fig_daily = px.line(
        daily_status,
        x="date",
        y="percentage",
        color="overall_status",
        markers=True,
        title="Tren Persentase Status Kualitas Air Harian"
    )

    st.plotly_chart(fig_daily, use_container_width=True)

    st.markdown(
        """
**Insight:** Visualisasi ini menunjukkan perubahan komposisi status kualitas air dari hari ke hari.
Jika persentase warning atau critical meningkat pada periode tertentu, maka periode tersebut perlu dianalisis lebih lanjut.
"""
    )

# ============================================================
# KESIMPULAN
# ============================================================

st.header("Kesimpulan Akhir")

st.markdown(
    f"""
Berdasarkan hasil analisis, kondisi kualitas air dapat dipantau melalui parameter utama yaitu
**Temperature, Dissolved Oxygen, pH, dan Turbidity**. Dari distribusi status, kategori yang paling dominan adalah
**{dominant_status}**.

Ditemukan **{anomaly_count:,}** data anomali turbidity, yang menunjukkan adanya lonjakan kekeruhan air
pada waktu tertentu. Analisis hubungan antar parameter menunjukkan bahwa kecepatan arus dan suhu dapat digunakan
untuk memahami perubahan kondisi perairan, meskipun kekuatan hubungannya perlu dilihat dari nilai korelasi.

Parameter yang paling sering memicu warning adalah **{top_warning_param}**, sehingga parameter tersebut perlu
menjadi prioritas dalam sistem pemantauan. Secara keseluruhan, dashboard ini dapat digunakan sebagai ringkasan
insight utama dan dasar pengambilan keputusan untuk pengembangan sistem early warning kualitas air.
"""
)

st.success("Dashboard selesai ditampilkan.")
