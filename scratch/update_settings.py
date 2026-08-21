import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import SchoolSetting, User

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

user = db.query(User).filter(User.email == "admin@school.edu").first()
setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == user.school_id).first()
setting.working_days = 6
setting.number_of_periods = 8
setting.max_weekly_teacher_periods = 40
db.commit()
print("Settings updated to 6 days, 8 periods (48 total).")
