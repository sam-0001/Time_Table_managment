import re

with open('app/api/routes/timetable.py', 'r') as f:
    content = f.read()

content = content.replace(
    'if current_user.school.plan_type != "DEMO":',
    'if current_user.school_plan != "DEMO":'
)

with open('app/api/routes/timetable.py', 'w') as f:
    f.write(content)
