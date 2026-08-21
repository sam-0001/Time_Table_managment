import os

def patch():
    with open('app/main.py', 'r') as f:
        content = f.read()
    
    # Import
    if "from app.api.routes import" in content:
        content = content.replace("from app.api.routes import auth, teachers, classes, subjects, timetable, leaves", "from app.api.routes import auth, teachers, classes, subjects, timetable, leaves, payments")
    
    # Include
    if "app.include_router(leaves.router, prefix='/api/leaves', tags=['leaves'])" in content:
        content = content.replace("app.include_router(leaves.router, prefix='/api/leaves', tags=['leaves'])", "app.include_router(leaves.router, prefix='/api/leaves', tags=['leaves'])\napp.include_router(payments.router, prefix='/api/payments', tags=['payments'])")
        
    with open('app/main.py', 'w') as f:
        f.write(content)

patch()
