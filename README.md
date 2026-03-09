# Proyek Analisis Data: E-Commerce Public Dataset

## Deskripsi

Proyek ini merupakan proyek akhir dari kelas **Belajar Fundamental Analisis Data** di Dicoding. Proyek ini bertujuan untuk menganalisis data E-Commerce Public Dataset (Olist - Brazilian E-Commerce) dan menyajikan hasil analisis melalui dashboard interaktif menggunakan Streamlit.

## Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv         # Data yang telah diproses untuk dashboard
│   ├── rfm_data.csv          # Data RFM Analysis
│   ├── city_orders.csv       # Data pesanan per kota
│   ├── seller_city_counts.csv # Data seller per kota
│   └── dashboard.py          # Streamlit Dashboard
├── data/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb            # Jupyter Notebook analisis data
├── README.md
├── requirements.txt
└── url.txt
```

## Instalasi

1. Clone repository ini atau download sebagai ZIP.

2. Install semua dependencies:

```bash
pip install -r requirements.txt
```

## Menjalankan Dashboard

1. Buka terminal dan navigasi ke folder `submission`:

```bash
cd submission
```

2. Jalankan dashboard:

```bash
streamlit run dashboard/dashboard.py
```

3. Dashboard akan terbuka di browser pada alamat `http://localhost:8501`.

## Analisis yang Dilakukan

### Pertanyaan Bisnis

1. **Bagaimana segmentasi pelanggan berdasarkan perilaku pembelian menggunakan RFM Analysis?**
2. **Bagaimana distribusi geografis pelanggan dan seller, serta pengaruh lokasi terhadap volume pesanan?**

### Teknik Analisis Lanjutan

- **RFM Analysis** — Segmentasi pelanggan berdasarkan Recency, Frequency, Monetary
- **Geospatial Analysis** — Visualisasi distribusi pelanggan dan seller menggunakan folium
- **Clustering (Binning)** — Pengelompokan segmen pelanggan berdasarkan aturan bisnis (tanpa ML)
