import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

tables = ['users', 'teachers', 'classes', 'divisions', 'subjects']

for table in tables:
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN is_demo BOOLEAN DEFAULT FALSE")
        print(f"Added is_demo to {table}")
    except Exception as e:
        print(f"Error adding to {table}: {e}")

cur.close()
conn.close()
