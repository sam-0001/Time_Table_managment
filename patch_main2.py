import re
with open("app/main.py", "r") as f:
    content = f.read()

content = content.replace(
    'from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export, payments',
    'from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export, payments, students, parents'
)

content = content.replace(
    'app.include_router(payments.router, prefix="/api/payments", tags=["payments"])',
    'app.include_router(payments.router, prefix="/api/payments", tags=["payments"])\napp.include_router(students.router, prefix="/api/students", tags=["students"])\napp.include_router(parents.router, prefix="/api/parents", tags=["parents"])'
)

with open("app/main.py", "w") as f:
    f.write(content)
