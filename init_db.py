# init_db.py (Improved Version)
import os
from sqlalchemy import create_engine, text
from src.models import Base
from dotenv import load_dotenv
import time

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def initialize_database():
    # Try connecting to the database, allow some time if it's not ready yet
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as connection:
                print("Database connection successful!")
                
                # Use an explicit transaction to create the extension
                trans = connection.begin()
                print("Attempting to create 'vector' extension...")
                connection.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
                trans.commit()
                print("'vector' extension created successfully or already exists.")
                
                # Now create all tables
                print("Creating all tables from models...")
                Base.metadata.create_all(engine)
                print("All tables created successfully.")
            
            break  # Exit the loop if successful

        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            retries -= 1
            print(f"Retrying in 5 seconds... ({retries} attempts left)")
            time.sleep(5)

if __name__ == "__main__":
    initialize_database()
