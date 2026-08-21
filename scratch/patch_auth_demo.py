import re

with open('app/api/routes/auth.py', 'r') as f:
    content = f.read()

# Import the demo data function at the top
if 'from app.core.demo_data import generate_demo_data' not in content:
    content = content.replace(
        'from app.api.deps import get_current_user',
        'from app.api.deps import get_current_user\nfrom app.core.demo_data import generate_demo_data'
    )

# Inject the hook before return user
hook_code = """    db.commit()
    db.refresh(user)
    
    db.refresh(academic_year)
    if school.plan_type == "DEMO":
        generate_demo_data(db, school.id, academic_year.id)
        
    return user"""

content = content.replace(
    '    db.commit()\n    db.refresh(user)\n    return user',
    hook_code
)

with open('app/api/routes/auth.py', 'w') as f:
    f.write(content)
