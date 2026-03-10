import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import st_folium

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_main_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

@st.cache_data
def load_rfm_data():
    return pd.read_csv("dashboard/rfm_data.csv")

@st.cache_data
def load_geo_data():
    city_orders = pd.read_csv("dashboard/city_orders.csv")
    seller_cities = pd.read_csv("dashboard/seller_city_counts.csv")
    return city_orders, seller_cities


main_df = load_main_data()
rfm_df = load_rfm_data()
city_orders_df, seller_cities_df = load_geo_data()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
st.sidebar.markdown("## 🛒 E-Commerce Dashboard")
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Data")

# Date range filter
min_date = main_df['order_purchase_timestamp'].min().date()
max_date = main_df['order_purchase_timestamp'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Rentang Tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# State filter
all_states = sorted(main_df['customer_state'].dropna().unique())
selected_states = st.sidebar.multiselect(
    "Pilih State",
    options=all_states,
    default=[]
)

# Apply filters
filtered_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) &
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
]
if selected_states:
    filtered_df = filtered_df[filtered_df['customer_state'].isin(selected_states)]

st.sidebar.markdown("---")
st.sidebar.markdown(f"📊 **Data ditampilkan:** {filtered_df.shape[0]:,} pesanan")

# ============================================================
# HEADER
# ============================================================
st.markdown('<p class="main-header">🛒 E-Commerce Public Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analisis Data E-Commerce Brazil (Olist) — RFM Analysis & Geospatial</p>', unsafe_allow_html=True)

# ============================================================
# KPI METRICS
# ============================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_orders = filtered_df['order_id'].nunique()
    st.metric("📦 Total Pesanan", f"{total_orders:,}")

with col2:
    total_revenue = filtered_df['payment_value'].sum()
    st.metric("💰 Total Revenue", f"R$ {total_revenue:,.0f}")

with col3:
    avg_order_value = filtered_df['payment_value'].mean()
    st.metric("💵 Rata-rata Nilai Pesanan", f"R$ {avg_order_value:,.2f}")

with col4:
    unique_customers = filtered_df['customer_unique_id'].nunique()
    st.metric("👥 Pelanggan Unik", f"{unique_customers:,}")

st.markdown("---")

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3 = st.tabs(["📈 Tren Pesanan", "🎯 RFM Analysis", "🗺️ Geospatial Analysis"])

# ============================================================
# TAB 1: ORDER TRENDS
# ============================================================
with tab1:
    st.subheader("Tren Pesanan Bulanan")

    # Monthly orders
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['order_month'] = filtered_df_copy['order_purchase_timestamp'].dt.to_period('M')
    monthly = filtered_df_copy.groupby('order_month').agg(
        total_orders=('order_id', 'count'),
        total_revenue=('payment_value', 'sum')
    ).reset_index()
    monthly['order_month'] = monthly['order_month'].astype(str)

    fig, ax1 = plt.subplots(figsize=(14, 5))
    color1 = '#2196F3'
    ax1.plot(monthly['order_month'], monthly['total_orders'],
             color=color1, linewidth=2.5, marker='o', markersize=5)
    ax1.set_xlabel('Bulan', fontsize=11)
    ax1.set_ylabel('Jumlah Pesanan', color=color1, fontsize=11)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.tick_params(axis='x', rotation=45)
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(2))

    color2 = '#FF9800'
    ax2 = ax1.twinx()
    ax2.fill_between(range(len(monthly)), monthly['total_revenue'],
                     alpha=0.25, color=color2)
    ax2.set_ylabel('Revenue (BRL)', color=color2, fontsize=11)
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title('Tren Pesanan & Revenue Bulanan', fontsize=15, fontweight='bold', pad=15)
    fig.tight_layout()
    st.pyplot(fig)

    # Top categories
    st.subheader("Top 10 Kategori Produk")
    st.info("📝 Data kategori produk dihitung berdasarkan seluruh dataset (tidak dipengaruhi filter tanggal).")

    # Load order_items and products for category analysis
    @st.cache_data
    def get_category_data():
        order_items = pd.read_csv("data/order_items_dataset.csv")
        products = pd.read_csv("data/products_dataset.csv")
        translations = pd.read_csv("data/product_category_name_translation.csv")
        items_products = order_items.merge(products[['product_id', 'product_category_name']], on='product_id', how='left')
        items_products = items_products.merge(translations, on='product_category_name', how='left')
        items_products['product_category_name_english'].fillna('other', inplace=True)
        return items_products

    items_products = get_category_data()
    cat_revenue = items_products.groupby('product_category_name_english')['price'].sum().sort_values(ascending=False).head(10)

    fig2, ax = plt.subplots(figsize=(12, 5))
    colors = sns.color_palette('Blues_r', 10)
    ax.barh(cat_revenue.index[::-1], cat_revenue.values[::-1], color=colors[::-1])
    ax.set_xlabel('Total Revenue (BRL)')
    ax.set_title('Top 10 Kategori Produk berdasarkan Revenue', fontsize=14, fontweight='bold')
    max_val = cat_revenue.values.max()
    for i, v in enumerate(cat_revenue.values[::-1]):
        ax.text(v + max_val * 0.01, i, f'R${v:,.0f}', va='center', fontsize=9)
    ax.set_xlim(right=max_val * 1.25)
    plt.tight_layout()
    st.pyplot(fig2)

# ============================================================
# TAB 2: RFM ANALYSIS
# ============================================================
with tab2:
    st.subheader("🎯 Segmentasi Pelanggan — RFM Analysis")
    st.markdown("""
    RFM Analysis mengelompokkan pelanggan berdasarkan:
    - **Recency:** Berapa hari sejak terakhir membeli
    - **Frequency:** Berapa kali membeli
    - **Monetary:** Berapa total belanja
    """)

    # Segment distribution
    segment_counts = rfm_df['segment'].value_counts()

    segment_colors = {
        'Champions': '#4CAF50',
        'Loyal Customers': '#8BC34A',
        'Potential Loyalists': '#03A9F4',
        'New Customers': '#00BCD4',
        'Need Attention': '#FFC107',
        'At Risk': '#FF9800',
        "Can't Lose Them": '#FF5722',
        'Hibernating': '#9E9E9E'
    }

    col1, col2 = st.columns(2)

    with col1:
        fig3, ax = plt.subplots(figsize=(8, 6))
        colors = [segment_colors.get(seg, '#9E9E9E') for seg in segment_counts.index[::-1]]
        ax.barh(segment_counts.index[::-1], segment_counts.values[::-1], color=colors)
        ax.set_xlabel('Jumlah Pelanggan')
        ax.set_title('Distribusi Segmen Pelanggan', fontsize=14, fontweight='bold')
        max_val = segment_counts.values.max()
        for i, v in enumerate(segment_counts.values[::-1]):
            ax.text(v + max_val * 0.02, i, f'{v:,} ({v/rfm_df.shape[0]*100:.1f}%)', va='center', fontsize=9)
        ax.set_xlim(right=max_val * 1.35)
        plt.tight_layout()
        st.pyplot(fig3)

    with col2:
        fig4, ax = plt.subplots(figsize=(8, 6))
        ax.pie(
            segment_counts.values,
            labels=segment_counts.index,
            colors=[segment_colors.get(seg, '#9E9E9E') for seg in segment_counts.index],
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85
        )
        centre_circle = plt.Circle((0, 0), 0.55, fc='white')
        ax.add_artist(centre_circle)
        ax.set_title('Proporsi Segmen', fontsize=14, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig4)

    # RFM metrics per segment
    st.subheader("📊 Rata-rata RFM Metrics per Segmen")

    segment_rfm = rfm_df.groupby('segment').agg(
        avg_recency=('recency', 'mean'),
        avg_frequency=('frequency', 'mean'),
        avg_monetary=('monetary', 'mean'),
        customer_count=('customer_unique_id', 'count')
    ).round(2).sort_values('avg_monetary', ascending=False)

    st.dataframe(
        segment_rfm.style.format({
            'avg_recency': '{:.0f} days',
            'avg_frequency': '{:.2f}',
            'avg_monetary': 'R$ {:.2f}',
            'customer_count': '{:,}'
        }),
        use_container_width=True
    )

# ============================================================
# TAB 3: GEOSPATIAL ANALYSIS
# ============================================================
with tab3:
    st.subheader("🗺️ Distribusi Geografis Pelanggan & Seller")
    st.markdown("Peta di bawah menunjukkan distribusi pelanggan (🔵 biru) dan seller (🔴 merah) di seluruh Brasil.")

    # Create folium map
    brazil_center = [-14.235, -51.9253]
    m = folium.Map(location=brazil_center, zoom_start=4, tiles='CartoDB positron')

    # Customer markers (top 50 cities)
    for _, row in city_orders_df.head(50).iterrows():
        folium.CircleMarker(
            location=[row['avg_lat'], row['avg_lng']],
            radius=max(3, min(row['total_orders'] / 200, 25)),
            color='#2196F3',
            fill=True,
            fill_color='#2196F3',
            fill_opacity=0.6,
            popup=f"{row['geolocation_city']}-{row['geolocation_state']}: {row['total_orders']:,} orders"
        ).add_to(m)

    # Seller markers (top 30 cities)
    for _, row in seller_cities_df.head(30).iterrows():
        folium.CircleMarker(
            location=[row['avg_lat'], row['avg_lng']],
            radius=max(3, min(row['total_sellers'] / 10, 20)),
            color='#FF5722',
            fill=True,
            fill_color='#FF5722',
            fill_opacity=0.6,
            popup=f"Sellers: {row['geolocation_city']}-{row['geolocation_state']}: {row['total_sellers']}"
        ).add_to(m)

    st_folium(m, width=None, height=500, use_container_width=True)

    # State bar charts
    st.subheader("📊 Top 10 States berdasarkan Volume Pesanan")

    state_data = filtered_df.groupby('customer_state').agg(
        total_orders=('order_id', 'count'),
        total_revenue=('payment_value', 'sum')
    ).reset_index().sort_values('total_orders', ascending=False).head(10)

    col1, col2 = st.columns(2)

    with col1:
        fig5, ax = plt.subplots(figsize=(8, 5))
        colors = sns.color_palette('Blues_r', 10)
        ax.barh(state_data['customer_state'][::-1], state_data['total_orders'][::-1], color=colors[::-1])
        ax.set_title('Jumlah Pesanan per State', fontsize=13, fontweight='bold')
        ax.set_xlabel('Jumlah Pesanan')
        max_val = state_data['total_orders'].max()
        for i, v in enumerate(state_data['total_orders'][::-1].values):
            ax.text(v + max_val * 0.01, i, f'{v:,}', va='center', fontsize=9)
        ax.set_xlim(right=max_val * 1.2)
        plt.tight_layout()
        st.pyplot(fig5)

    with col2:
        fig6, ax = plt.subplots(figsize=(8, 5))
        colors = sns.color_palette('Oranges_r', 10)
        ax.barh(state_data['customer_state'][::-1], state_data['total_revenue'][::-1], color=colors[::-1])
        ax.set_title('Revenue per State (BRL)', fontsize=13, fontweight='bold')
        ax.set_xlabel('Revenue (BRL)')
        max_val = state_data['total_revenue'].max()
        for i, v in enumerate(state_data['total_revenue'][::-1].values):
            ax.text(v + max_val * 0.01, i, f'R${v:,.0f}', va='center', fontsize=9)
        ax.set_xlim(right=max_val * 1.25)
        plt.tight_layout()
        st.pyplot(fig6)


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 0.85rem;">
        <p>© 2025 E-Commerce Public Dashboard | Proyek Analisis Data - Dicoding</p>
        <p>Dataset: <a href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce" target="_blank">Brazilian E-Commerce by Olist</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
