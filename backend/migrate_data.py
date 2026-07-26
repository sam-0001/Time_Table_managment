import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

sqlite_url = "sqlite:///./sql_app.db"
postgres_url = "postgresql://postgres:TimeTable#1100@db.ujdutvrmljeoczzelprd.supabase.co:5432/postgres"

# Engines
sqlite_engine = create_engine(sqlite_url)
postgres_engine = create_engine(postgres_url)

# Reflect metadata from both
sqlite_meta = MetaData()
sqlite_meta.reflect(bind=sqlite_engine)

postgres_meta = MetaData()
postgres_meta.reflect(bind=postgres_engine)

tables = [
    "users",
    "school_settings",
    "teachers",
    "classes",
    "divisions",
    "subjects",
    "teacher_subjects",
    "timetable_slots",
    "teacher_leaves"
]

from sqlalchemy import create_engine, MetaData, text

with postgres_engine.connect() as pg_conn:
    # Disable foreign key checks temporarily in Postgres
    try:
        pg_conn.execute(text("SET session_replication_role = 'replica';"))
    except Exception as e:
        print(f"Could not set replication role: {e}")
        pass

    for table_name in tables:
        if table_name not in sqlite_meta.tables:
            continue
            
        print(f"Migrating {table_name}...")
        sqlite_table = sqlite_meta.tables[table_name]
        postgres_table = postgres_meta.tables[table_name]
        
        # Read from SQLite
        with sqlite_engine.connect() as sq_conn:
            result = sq_conn.execute(sqlite_table.select())
            rows = [dict(row._mapping) for row in result]
            
        if rows:
            # Delete existing in Postgres just in case
            pg_conn.execute(postgres_table.delete())
            # Insert into Postgres
            pg_conn.execute(postgres_table.insert(), rows)
            print(f" -> Inserted {len(rows)} rows into {table_name}")
            
    try:
        pg_conn.execute("SET session_replication_role = 'origin';")
    except Exception:
        pass
        
print("Migration completed successfully!")
