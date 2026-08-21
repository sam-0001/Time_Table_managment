import sys

def patch():
    with open('app/main.py', 'r') as f:
        content = f.read()

    old = "from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export, payments, admin_migrate"
    new = "from app.api.routes import auth, school, teachers, subjects, classes, timetable, leaves, import_export, payments"
    content = content.replace(old, new)
    
    old_include = 'app.include_router(admin_migrate.router, prefix="/api/admin", tags=["admin"])'
    content = content.replace(old_include, "")
    
    with open('app/main.py', 'w') as f:
        f.write(content)

patch()
