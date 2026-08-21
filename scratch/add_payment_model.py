import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine, text

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)

with engine.begin() as conn:
    print("Creating payments table...")
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS payments (
        order_id VARCHAR PRIMARY KEY,
        school_id VARCHAR NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
        amount FLOAT NOT NULL,
        status VARCHAR DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """))
    print("Done!")
