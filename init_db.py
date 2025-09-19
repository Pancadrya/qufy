# init_db.py (Versi Perbaikan)
import os
from sqlalchemy import create_engine, text
from src.models import Base
from dotenv import load_dotenv
import time

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def initialize_database():
    # Coba hubungkan ke database, beri waktu jika belum siap
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as connection:
                print("Koneksi database berhasil!")
                
                # Gunakan transaksi eksplisit untuk membuat ekstensi
                trans = connection.begin()
                print("Mencoba membuat ekstensi 'vector'...")
                connection.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
                trans.commit()
                print("Ekstensi 'vector' berhasil dibuat atau sudah ada.")
                
                # Sekarang buat semua tabel
                print("Membuat semua tabel dari models...")
                Base.metadata.create_all(engine)
                print("Semua tabel berhasil dibuat.")
            
            break # Keluar dari loop jika berhasil

        except Exception as e:
            print(f"Gagal terhubung ke database: {e}")
            retries -= 1
            print(f"Mencoba lagi dalam 5 detik... ({retries} percobaan tersisa)")
            time.sleep(5)

if __name__ == "__main__":
    initialize_database()