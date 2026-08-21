import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import Teacher

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

teachers = db.query(Teacher).all()
for t in teachers:
    print(f"Teacher {t.id} max_daily: {t.max_daily_periods}, max_weekly: {t.max_weekly_periods}")

