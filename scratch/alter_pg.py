import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.sql import text

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)

with engine.begin() as conn:
    print("Altering tables in Supabase Postgres...")
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE"))
        conn.execute(text("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE"))
        conn.execute(text("ALTER TABLE classrooms ADD COLUMN IF NOT EXISTS school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE"))
        
        # Get the first school ID to assign to existing rows
        res = conn.execute(text("SELECT id FROM schools LIMIT 1")).fetchone()
        if res:
            school_id = res[0]
            print(f"Setting default school_id to {school_id}")
            conn.execute(text("UPDATE users SET school_id = :sid WHERE school_id IS NULL"), {"sid": school_id})
            conn.execute(text("UPDATE teachers SET school_id = :sid WHERE school_id IS NULL"), {"sid": school_id})
            conn.execute(text("UPDATE classrooms SET school_id = :sid WHERE school_id IS NULL"), {"sid": school_id})
        
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
