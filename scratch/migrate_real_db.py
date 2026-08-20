import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import make_transient
from app.db.database import Base
from app.db.models import TimetableSlot

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
sqlite_url = "sqlite:////Users/sohamchaudhari/Desktop/Time_Table/backend/sql_app.db"

pg_engine = create_engine(postgres_url)
sqlite_engine = create_engine(sqlite_url)

PgSession = sessionmaker(bind=pg_engine)
SqliteSession = sessionmaker(bind=sqlite_engine)

pg_session = PgSession()
sqlite_session = SqliteSession()

# DELETE rows instead of dropping table
pg_session.query(TimetableSlot).delete()
pg_session.commit()

models_to_migrate = [TimetableSlot]

for model in models_to_migrate:
    print(f"Migrating {model.__tablename__} (row by row)...")
    items = sqlite_session.query(model).all()
    successful = 0
    failed = 0
    for item in items:
        try:
            make_transient(item)
            pg_session.add(item)
            pg_session.commit()
            successful += 1
        except Exception as e:
            pg_session.rollback()
            failed += 1
    print(f"{model.__tablename__}: {successful} migrated, {failed} failed.")

print("Migration completed!")
