# Gunakan base image Python yang ringan
FROM python:3.11-slim

# Tetapkan direktori kerja di dalam container
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching
COPY requirements.txt .

# Install semua library yang dibutuhkan
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file proyek (app.py, dll) ke dalam container
COPY . .

# Beri tahu Docker bahwa container akan berjalan di port 8501
EXPOSE 8501

# Perintah untuk menjalankan aplikasi saat container dimulai
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]