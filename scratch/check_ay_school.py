import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.sql import text

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)

with engine.begin() as conn:
    res = conn.execute(text("SELECT id, name, school_id FROM academic_years")).fetchall()
    print("Academic Years:")
    for r in res:
        print(r)
    
    res2 = conn.execute(text("SELECT id, name, school_id FROM classes")).fetchall()
    print("Classes:")
    for r in res2:
        print(r)
