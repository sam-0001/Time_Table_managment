import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import Session
from app.db.database import Base
from app.db.models import *

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

print("Wiping all data from all tables...")
with engine.connect() as con:
    con.execute(text("TRUNCATE TABLE users, schools, school_settings, academic_years, teachers, classes, divisions, subjects, teacher_subjects, teacher_leaves, timetable_slots, substitutions, otp_codes CASCADE;"))
    con.commit()

print("All tables truncated successfully.")

from app.api.routes.auth import register_school
from app.schemas.user import SchoolRegisterCreate

user_in = SchoolRegisterCreate(
    school_name="smt P.D. Badola,High School",
    full_name="Sunil Chaudhari",
    email="sc922467@gmail.com",
    password="Sunil@123"
)

try:
    user = register_school(user_in=user_in, db=db)
    print(f"Created new school and user: {user.email}")
except Exception as e:
    print(f"Error creating user: {e}")
