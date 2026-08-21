import re

with open('app/core/demo_data.py', 'r') as f:
    content = f.read()

content = content.replace(
    'employee_id=f"DEMO-{subj_code}"',
    'employee_id=f"DEMO-{subj_code}-{school_id[:8]}"'
)

with open('app/core/demo_data.py', 'w') as f:
    f.write(content)
