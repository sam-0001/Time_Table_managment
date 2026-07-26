from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the School Timetable Management System API"}
