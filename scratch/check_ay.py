import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.sql import text

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)

with engine.begin() as conn:
    print("Checking academic years...")
    res = conn.execute(text("SELECT id, name, is_active FROM academic_years")).fetchall()
    print(res)
    if not any(r[2] for r in res):
        print("No active academic year found! Setting the first one to active.")
        if res:
            conn.execute(text("UPDATE academic_years SET is_active = True WHERE id = :id"), {"id": res[0][0]})
            print("Done!")
