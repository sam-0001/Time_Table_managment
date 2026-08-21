import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine, text

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)

with engine.begin() as conn:
    print("Altering tables to support Demo Mode and Payments...")
    conn.execute(text("ALTER TABLE schools ADD COLUMN IF NOT EXISTS plan_type VARCHAR DEFAULT 'DEMO';"))
    conn.execute(text("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE;"))
    conn.execute(text("ALTER TABLE classes ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE;"))
    conn.execute(text("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE;"))
    conn.execute(text("ALTER TABLE divisions ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE;"))
    
    # Set the creator to PRO
    conn.execute(text("UPDATE schools SET plan_type = 'PRO' WHERE id IN (SELECT school_id FROM users WHERE email = 'sc922467@gmail.com');"))
    print("Done!")
