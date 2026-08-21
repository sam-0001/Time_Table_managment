from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export, payments, admin_migrate

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
app.include_router(admin_migrate.router, prefix="/api/admin", tags=["admin"])

from sqlalchemy import text
from app.db.database import SessionLocal

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
