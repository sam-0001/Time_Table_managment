import re

with open('app/core/demo_data.py', 'r') as f:
    content = f.read()

old = 'email=f"demo_{subj_code.lower()}@demo.com"'
new = 'email=f"demo_{subj_code.lower()}_{school_id[:8]}@demo.com"'
content = content.replace(old, new)

with open('app/core/demo_data.py', 'w') as f:
    f.write(content)
