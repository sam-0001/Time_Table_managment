from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export, payments, students, parents, attendance

app = FastAPI(
    title="School Timetable Management System API",
    description="Production-ready API for managing school timetables",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(school.router, prefix="/api/school", tags=["school"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["teachers"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["subjects"])
app.include_router(classes.router, prefix="/api/classes", tags=["classes"])
app.include_router(timetable.router, prefix="/api/timetable", tags=["timetable"])
app.include_router(leaves.router, prefix="/api/leaves", tags=["leaves"])
app.include_router(import_export.router, prefix="/api/import-export", tags=["import-export"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(parents.router, prefix="/api/parents", tags=["parents"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])


from sqlalchemy import text
from app.db.database import SessionLocal, engine, SQLALCHEMY_DATABASE_URL

def run_startup_migrations():
    """Run safe, idempotent migrations on startup to add missing tables/columns."""
    is_postgres = "postgresql" in SQLALCHEMY_DATABASE_URL or "postgres" in SQLALCHEMY_DATABASE_URL
    is_sqlite = "sqlite" in SQLALCHEMY_DATABASE_URL

    db = SessionLocal()
    try:
        if is_postgres:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS payments (
                    order_id VARCHAR PRIMARY KEY,
                    school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE,
                    amount FLOAT NOT NULL,
                    status VARCHAR DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            db.execute(text("ALTER TABLE schools ADD COLUMN IF NOT EXISTS plan_type VARCHAR DEFAULT 'FREE'"))
            db.execute(text("ALTER TABLE schools ADD COLUMN IF NOT EXISTS available_generations INTEGER DEFAULT 0"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR"))

            # Add roles if Postgres
            try:
                db.execute(text("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'STUDENT'"))
                db.execute(text("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'PARENT'"))
                db.commit()
            except Exception as e:
                db.rollback()
                pass # might fail if not postgres or already exists or transaction issue
                
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS parents (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE,
                    phone VARCHAR,
                    address VARCHAR,
                    blood_group VARCHAR
                )
            '''))
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS students (
                    id VARCHAR PRIMARY KEY,
                    user_id VARCHAR UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE,
                    parent_id VARCHAR REFERENCES parents(id) ON DELETE SET NULL,
                    division_id VARCHAR REFERENCES divisions(id) ON DELETE SET NULL,
                    admission_number VARCHAR,
                    gender VARCHAR,
                    date_of_birth TIMESTAMP,
                    blood_group VARCHAR,
                    address VARCHAR
                )
            '''))

            db.execute(text("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE"))
            db.execute(text("ALTER TABLE classes ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE"))
            db.execute(text("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE"))
            db.execute(text("UPDATE schools SET plan_type = 'FREE' WHERE plan_type IS NULL"))
        elif is_sqlite:
            # SQLite: use try/except per statement since IF NOT EXISTS isn't supported for columns
            for stmt in [
                "CREATE TABLE IF NOT EXISTS payments (order_id TEXT PRIMARY KEY, school_id TEXT, amount REAL NOT NULL, status TEXT DEFAULT 'PENDING', created_at TEXT)",
                "ALTER TABLE schools ADD COLUMN plan_type TEXT DEFAULT 'FREE'",
                "ALTER TABLE schools ADD COLUMN available_generations INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN is_demo INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN phone TEXT",
                "ALTER TABLE teachers ADD COLUMN is_demo INTEGER DEFAULT 0",
                "ALTER TABLE classes ADD COLUMN is_demo INTEGER DEFAULT 0",
                "ALTER TABLE subjects ADD COLUMN is_demo INTEGER DEFAULT 0",
            ]:
                try:
                    db.execute(text(stmt))
                except Exception:
                    pass  # Already exists
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[startup] Migration warning (non-fatal): {e}")
    finally:
        db.close()

# Run migrations on startup (safe, idempotent)
run_startup_migrations()

@app.get("/api/health")
def health_check():
    try:
        # Query the database to keep Supabase active
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "message": "Database is active"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"message": "Welcome to the School Timetable Management System API"}
