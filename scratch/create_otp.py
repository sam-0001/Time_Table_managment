import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from app.db.models import OTPCode

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
OTPCode.__table__.create(engine, checkfirst=True)
print("Created otp_codes table.")
