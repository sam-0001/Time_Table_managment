import re
with open("app/main.py", "r") as f:
    content = f.read()

migration_sql = """
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS attendances (
                    id VARCHAR PRIMARY KEY,
                    school_id VARCHAR REFERENCES schools(id) ON DELETE CASCADE,
                    student_id VARCHAR REFERENCES students(id) ON DELETE CASCADE,
                    division_id VARCHAR REFERENCES divisions(id) ON DELETE CASCADE,
                    recorded_by_id VARCHAR REFERENCES users(id) ON DELETE SET NULL,
                    date TIMESTAMP NOT NULL,
                    status VARCHAR DEFAULT 'PRESENT',
                    remarks VARCHAR
                )
            '''))
"""

content = content.replace(
    'date_of_birth TIMESTAMP,\n                    blood_group VARCHAR,\n                    address VARCHAR\n                )\n            \'\'))',
    'date_of_birth TIMESTAMP,\n                    blood_group VARCHAR,\n                    address VARCHAR\n                )\n            \'\'))\n' + migration_sql
)

content = content.replace(
    'from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export, payments, students, parents',
    'from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export, payments, students, parents, attendance'
)

content = content.replace(
    'app.include_router(parents.router, prefix="/api/parents", tags=["parents"])',
    'app.include_router(parents.router, prefix="/api/parents", tags=["parents"])\napp.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])'
)

with open("app/main.py", "w") as f:
    f.write(content)
