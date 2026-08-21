import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine, text

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)

with engine.begin() as conn:
    print("Adding available_generations to schools...")
    conn.execute(text("ALTER TABLE schools ADD COLUMN IF NOT EXISTS available_generations INTEGER DEFAULT 0;"))
    
    # Set creator to 999999 (Unlimited)
    conn.execute(text("UPDATE schools SET available_generations = 999999 WHERE id IN (SELECT school_id FROM users WHERE email = 'sc922467@gmail.com');"))
    print("Done!")
