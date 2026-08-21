import sys

def patch():
    with open('app/db/models.py', 'r') as f:
        content = f.read()

    old = 'created_at = Column(DateTime, default=datetime.utcnow)'
    new = 'created_at = Column(DateTime, default=datetime.utcnow)\n    school = relationship("School")'
    if 'school = relationship("School")' not in content:
        content = content.replace(old, new)
        with open('app/db/models.py', 'w') as f:
            f.write(content)

patch()
