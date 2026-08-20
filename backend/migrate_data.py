from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

SQLITE_URL = "sqlite:///./sql_app.db"
POSTGRES_URL = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"

sqlite_engine = create_engine(SQLITE_URL)
postgres_engine = create_engine(POSTGRES_URL)

sqlite_meta = MetaData()
sqlite_meta.reflect(bind=sqlite_engine)

postgres_meta = MetaData()
postgres_meta.reflect(bind=postgres_engine)

SqliteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)

tables = [
    "users", "schools", "academic_years", "school_settings",
    "classes", "classrooms", "teachers", "divisions",
    "subjects", "teacher_subjects", "timetable_slots",
    "teacher_leaves", "substitutions", "audit_logs"
]

def migrate_data():
    sqlite_session = SqliteSession()
    postgres_session = PostgresSession()

    try:
        for table_name in tables:
            if table_name not in sqlite_meta.tables:
                continue
            
            print(f"Migrating {table_name}...")
            sqlite_table = sqlite_meta.tables[table_name]
            postgres_table = postgres_meta.tables[table_name]

            postgres_session.execute(postgres_table.delete())

            rows = sqlite_session.execute(sqlite_table.select()).fetchall()
            
            if rows:
                dicts = [dict(row._mapping) for row in rows]
                postgres_session.execute(postgres_table.insert(), dicts)
                print(f"  Inserted {len(rows)} records into {table_name}.")
            else:
                print(f"  No records found for {table_name}.")
        
        postgres_session.commit()
        print("Migration complete!")
    except Exception as e:
        postgres_session.rollback()
        print(f"An error occurred: {e}")
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    migrate_data()
