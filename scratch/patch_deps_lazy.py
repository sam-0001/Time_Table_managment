import re

with open('app/api/deps.py', 'r') as f:
    content = f.read()

content = content.replace(
    '        db.expunge(user)',
    '        _ = user.school # trigger lazy load before expunging\n        db.expunge(user)'
)

with open('app/api/deps.py', 'w') as f:
    f.write(content)
