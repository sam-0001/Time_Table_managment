import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import SchoolClass, AcademicYear, User

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

# Get admin user
user = db.query(User).filter(User.email == "admin@school.edu").first()
print(f"User school ID: {user.school_id}")

classes = db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == user.school_id).all()
print(f"Classes for user: {len(classes)}")

# Also with academic_year_id filter
classes_filtered = db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == user.school_id, SchoolClass.academic_year_id == 'temp-academic-year-id').all()
print(f"Classes filtered: {len(classes_filtered)}")
