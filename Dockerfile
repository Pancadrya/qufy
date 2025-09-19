# Dockerfile

# Gunakan base image Python versi 3.11
FROM python:3.11-slim

# Tetapkan direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt terlebih dahulu untuk caching
COPY requirements.txt .

# Install semua dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file dari proyek ke dalam direktori kerja di container
COPY . .

# Ekspos port yang digunakan oleh Streamlit
EXPOSE 8501

# Perintah default untuk menjalankan aplikasi saat container dimulai
CMD ["streamlit", "run", "app.py"]