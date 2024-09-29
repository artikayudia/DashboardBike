import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

day = pd.read_csv("day.csv")
hour = pd.read_csv("hour.csv")

# Menambahkan kolom tahun ke DataFrame
day['year'] = pd.to_datetime(day['dteday']).dt.year
hour['year'] = pd.to_datetime(hour['dteday']).dt.year

st.sidebar.header('Filter Data Penyewaan')

# Pilih tahun di sidebar
selected_year = st.sidebar.selectbox(
    'Pilih Tahun',
    options=sorted(day['year'].unique()),  # Daftar tahun unik yang tersedia
    index=len(day['year'].unique()) - 1  # Indeks tahun terakhir sebagai default
)

# Definisi variabel tanggal minimum dan maksimum
min_date = pd.to_datetime(day['dteday']).dt.date.min()
max_date = pd.to_datetime(day['dteday']).dt.date.max()

# Menampilkan nilai min dan max untuk debugging
st.sidebar.write(f'Min Tanggal: {min_date}')
st.sidebar.write(f'Max Tanggal: {max_date}')

# Input rentang tanggal di sidebar
start_date, end_date = st.sidebar.date_input(
    label='Pilih Tanggal Penyewaan',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Filter data berdasarkan tahun dan tanggal
filtered_df = day[(pd.to_datetime(day['dteday']).dt.date >= start_date) & 
                  (pd.to_datetime(day['dteday']).dt.date <= end_date) & 
                  (day['year'] == selected_year)]

# Cek jika filtered_df kosong
if filtered_df.empty:
    st.warning("Tidak ada data untuk rentang tanggal dan tahun yang dipilih.")
else:
    # Menyiapkan data berdasarkan season
    season_dict = {1: 'Clear/Few Clouds', 2: 'Mist/Cloudy', 3: 'Light Rain/Snow'}
    filtered_df['season_label'] = filtered_df['season'].replace(season_dict)

    # Judul Dashboard
    st.title("Dashboard Penyewaan Sepeda")

    # Metrics untuk menampilkan informasi penyewaan
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pengguna Biasa", filtered_df['casual'].sum())
    with col2:
        st.metric("Pengguna Terdaftar", filtered_df['registered'].sum())
    with col3:
        st.metric("Total Penyewa", filtered_df['cnt'].sum())

    # Pengaruh Cuaca terhadap Jumlah Pengguna Kasual dan Terdaftar
    weather_conditions = { 
        1: 'Clear/Few Clouds',
        2: 'Mist/Cloudy',
        3: 'Light Rain/Snow'
    }

    # Mengubah kolom 'weathersit' menjadi label yang lebih informatif
    day['weathersit'] = day['weathersit'].map(weather_conditions)

    # Menghitung total penyewaan berdasarkan kondisi cuaca untuk pengguna kasual dan terdaftar
    weather_usage = day.groupby('weathersit').agg({
        'casual': 'sum',
        'registered': 'sum',
        'cnt': 'sum'
    }).reset_index()

    # Visualisasi menggunakan bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    weather_usage.set_index('weathersit').plot(kind='bar', ax=ax)
    plt.title('Penggunaan Sepeda Berdasarkan Kondisi Cuaca')
    plt.xlabel('Kondisi Cuaca')
    plt.ylabel('Jumlah Penyewaan')
    plt.xticks(rotation=45)
    plt.legend(title='Tipe Pengguna', labels=['Pengguna Kasual', 'Pengguna Terdaftar', 'Total Penyewaan'])
    plt.grid(axis='y')
    plt.tight_layout()
    st.subheader("Pengaruh Cuaca terhadap Jumlah Pengguna Kasual dan Terdaftar")
    st.pyplot(fig)

    # Perbandingan Penggunaan Sepeda pada Hari Libur dan Hari Kerja
    st.subheader('Perbandingan Penggunaan Sepeda pada Hari Libur dan Hari Kerja')
    holiday_usage = day.groupby('holiday')['cnt'].sum().reset_index()
    holiday_usage.columns = ['Holiday', 'Total Usage']
    holiday_usage['Holiday'] = holiday_usage['Holiday'].map({0: 'Working Day', 1: 'Holiday'})
    plt.figure(figsize=(8, 5))
    plt.bar(holiday_usage['Holiday'], holiday_usage['Total Usage'], color=['blue', 'orange'])
    plt.title('Perbandingan Penggunaan Sepeda pada Hari Libur dan Hari Kerja')
    plt.xlabel('Status Hari')
    plt.ylabel('Total Penyewaan Sepeda')
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(plt) 

    # Analisis Hubungan Suhu dengan Penyewaan
    st.subheader("Perbandingan Penggunaan Sepeda per Jam: Hari Kerja vs Akhir Pekan")
    working_days = hour[hour['workingday'] == 1]
    hourly_usage_working = working_days.groupby('hr')['cnt'].sum().reset_index()
    weekend_days = hour[hour['workingday'] == 0]
    hourly_usage_weekend = weekend_days.groupby('hr')['cnt'].sum().reset_index()
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_usage_working['hr'], hourly_usage_working['cnt'], marker='o', label='Hari Kerja', color='blue')
    plt.plot(hourly_usage_weekend['hr'], hourly_usage_weekend['cnt'], marker='o', label='Akhir Pekan', color='orange')
    plt.title('Perbandingan Penggunaan Sepeda per Jam: Hari Kerja vs Akhir Pekan')
    plt.xlabel('Jam')
    plt.ylabel('Jumlah Penggunaan Sepeda')
    plt.xticks(hourly_usage_working['hr'])
    plt.legend()
    plt.grid()
    st.pyplot(plt)
