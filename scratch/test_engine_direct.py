import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import User, AcademicYear
from app.api.routes.timetable import generate_timetable

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)
user = db.query(User).filter(User.email == "admin@school.edu").first()
ay = db.query(AcademicYear).filter(AcademicYear.school_id == user.school_id).first()

try:
    res = generate_timetable(academic_year_id="temp-academic-year-id", db=db, current_user=user)
    print(res)
except Exception as e:
    print(f"Error: {e.detail if hasattr(e, 'detail') else e}")
