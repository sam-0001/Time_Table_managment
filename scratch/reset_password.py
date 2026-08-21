import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import User
from app.core.security import get_password_hash

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

new_password = "Sunil@01"
hashed = get_password_hash(new_password)

user = db.query(User).filter(User.email == "sc922467@gmail.com").first()
if user:
    user.hashed_password = hashed
    db.commit()
    print("✅ Password successfully updated for sc922467@gmail.com")
else:
    print("❌ User not found in the database!")

