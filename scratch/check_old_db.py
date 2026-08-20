import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine, text

old_url = "postgresql://postgres:TimeTable#1100@db.ujdutvrmljeoczzelprd.supabase.co:5432/postgres"
engine = create_engine(old_url)
with engine.connect() as conn:
    res = conn.execute(text("SELECT count(*) FROM users;")).scalar()
    print("Old DB users:", res)
    res = conn.execute(text("SELECT count(*) FROM teachers;")).scalar()
    print("Old DB teachers:", res)
    res = conn.execute(text("SELECT count(*) FROM subjects;")).scalar()
    print("Old DB subjects:", res)
