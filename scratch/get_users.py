import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import User

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
Session = sessionmaker(bind=engine)
session = Session()

users = session.query(User).all()
for u in users:
    print(f"ID: {u.id} | Email: {u.email} | Name: {u.full_name} | Role: {u.role}")
