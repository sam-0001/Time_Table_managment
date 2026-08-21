import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import SchoolClass, AcademicYear, User

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

user = db.query(User).filter(User.school_id == '7ae4f43f-289b-4c23-8fce-80e871ae7cda').first()
if user:
    print(f"User email: {user.email}, school ID: {user.school_id}")
    classes = db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == user.school_id).all()
    print(f"Classes for this user: {len(classes)}")
    
    for c in classes:
        print(c.name, c.academic_year_id)
else:
    print("No user found for that school.")
