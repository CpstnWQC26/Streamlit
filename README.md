# Aqua Monitoring Dashboard Streamlit

## Deskripsi Singkat Proyek

Aqua Monitoring Dashboard merupakan aplikasi berbasis Streamlit yang digunakan untuk memantau dan menganalisis kualitas air berdasarkan data yang telah diproses.

Dashboard ini menyediakan visualisasi interaktif untuk membantu pengguna memahami kondisi kualitas air serta mendukung pengambilan keputusan berbasis data.

---

## Fitur Utama

- Visualisasi data kualitas air
- Monitoring parameter kualitas air
- Analisis data interaktif
- Dashboard berbasis web menggunakan Streamlit

---

## Struktur Proyek

```text
.
├── app.py
├── dataset.csv
├── water_quality_ready.csv
├── requirements.txt
└── README.md
```

---

## Setup Environment

### Clone Repository

```bash
git clone <repository-url>
cd Streamlit
```

### Membuat Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependensi

```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan Aplikasi

Jalankan perintah berikut:

```bash
streamlit run app.py
```

Setelah berhasil dijalankan, aplikasi dapat diakses melalui browser pada alamat lokal yang diberikan oleh Streamlit.

---

## Dashboard Online

Dashboard dapat diakses melalui:

https://aquamonitoring.streamlit.app/

---

## Dataset

Dataset yang digunakan dalam dashboard:

- dataset.csv
- water_quality_ready.csv

---

## Dependensi

Seluruh dependensi proyek tersedia pada file:

```text
requirements.txt
```

---

