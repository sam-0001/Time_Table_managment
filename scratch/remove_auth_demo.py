import re

with open('app/api/routes/auth.py', 'r') as f:
    content = f.read()

# Remove the hook
old_hook = """    db.refresh(academic_year)
    if school.plan_type == "DEMO":
        generate_demo_data(db, school.id, academic_year.id)
        
    return user"""
new_hook = """    return user"""
content = content.replace(old_hook, new_hook)

with open('app/api/routes/auth.py', 'w') as f:
    f.write(content)
