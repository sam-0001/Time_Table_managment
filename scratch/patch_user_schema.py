import re

with open('app/schemas/user.py', 'r') as f:
    content = f.read()

content = content.replace(
    'school_plan: Optional[str] = None',
    'school_plan: Optional[str] = None\n    is_demo_mode: Optional[bool] = False'
)

with open('app/schemas/user.py', 'w') as f:
    f.write(content)
