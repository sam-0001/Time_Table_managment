import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

url_tx = "postgresql://postgres.lxczvmpobvblymkuukim:TimeTable%231100@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

engine = create_engine(url_tx)
Session = sessionmaker(bind=engine)
session = Session()

try:
    print("Testing query on TX mode...")
    res = session.execute(text("SELECT 1")).scalar()
    print(f"Result 1: {res}")
    res2 = session.execute(text("SELECT 1")).scalar()
    print(f"Result 2: {res2}")
    
    # Try a parameter query
    res3 = session.execute(text("SELECT :val"), {"val": 5}).scalar()
    print(f"Result 3: {res3}")
except Exception as e:
    print(f"Query failed: {e}")
