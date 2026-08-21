import re

with open('app/api/routes/auth.py', 'r') as f:
    content = f.read()

# Change school = School(name=user_in.school_name) to include plan_type="FREE"
content = content.replace(
    'school = School(name=user_in.school_name)',
    'school = School(name=user_in.school_name, plan_type="FREE")'
)

with open('app/api/routes/auth.py', 'w') as f:
    f.write(content)
