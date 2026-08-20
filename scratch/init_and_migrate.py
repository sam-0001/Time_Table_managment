import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import create_engine
from app.db.database import Base
from app.db.models import *

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"

engine = create_engine(postgres_url)
print("Creating tables in Postgres...")
Base.metadata.create_all(engine)
print("Tables created.")
