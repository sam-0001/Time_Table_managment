import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import SchoolClass, AcademicYear, User

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

# Get the new user
user = db.query(User).filter(User.email != "admin@school.edu").first()
ay = db.query(AcademicYear).filter(AcademicYear.school_id == user.school_id).first()

# Are there any classes that have temp-academic-year-id but were created recently?
# We can't know who created them. If they created them, we can just move all classes to the active one for testing? No, old user needs them!
classes = db.query(SchoolClass).all()
print(f"Total classes in DB: {len(classes)}")
