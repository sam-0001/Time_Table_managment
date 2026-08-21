import sys

def patch():
    with open('app/db/models.py', 'r') as f:
        content = f.read()

    old = "from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Time, Enum, DateTime, Text, JSON, UniqueConstraint"
    new = "from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Time, Enum, DateTime, Text, JSON, UniqueConstraint, Float"
    content = content.replace(old, new)
    
    with open('app/db/models.py', 'w') as f:
        f.write(content)

patch()
