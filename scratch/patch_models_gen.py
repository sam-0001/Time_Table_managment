import sys

def patch():
    with open('app/db/models.py', 'r') as f:
        content = f.read()

    old = 'plan_type = Column(String, default="DEMO")'
    new = 'plan_type = Column(String, default="DEMO")\n    available_generations = Column(Integer, default=0)'
    
    if new not in content:
        content = content.replace(old, new)
        with open('app/db/models.py', 'w') as f:
            f.write(content)

patch()
