import sys
import os
import requests
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import User, AcademicYear

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)
user = db.query(User).filter(User.email == "admin@school.edu").first()
from app.core.security import create_access_token
token = create_access_token({"sub": user.id, "role": user.role.value})

url = "https://time-table-managment-smoky.vercel.app/api/timetable/generate?academic_year_id=temp-academic-year-id"
headers = {"Authorization": f"Bearer {token}"}

res = requests.post(url, headers=headers)
print(res.status_code)
print(res.text)
