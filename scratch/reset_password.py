import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import User
from app.core.security import get_password_hash

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
Session = sessionmaker(bind=engine)
session = Session()

user = session.query(User).filter(User.email == "admin@school.edu").first()
if user:
    user.hashed_password = get_password_hash("admin123")
    session.commit()
    print("Password reset successfully for admin@school.edu to: admin123")
else:
    print("User not found.")
