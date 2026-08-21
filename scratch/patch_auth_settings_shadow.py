import re

with open('app/api/routes/auth.py', 'r') as f:
    content = f.read()

content = content.replace(
    'settings = SchoolSetting(',
    'school_setting = SchoolSetting('
)
content = content.replace(
    'db.add(settings)',
    'db.add(school_setting)'
)

with open('app/api/routes/auth.py', 'w') as f:
    f.write(content)
