import re

with open('app/db/models.py', 'r') as f:
    content = f.read()

# Add plan_type and available_generations to School
old_school = """class School(Base):
    __tablename__ = "schools"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    address = Column(String)"""

new_school = """class School(Base):
    __tablename__ = "schools"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    address = Column(String)
    plan_type = Column(String, default="DEMO") # "DEMO" or "PRO"
    available_generations = Column(Integer, default=0)"""

content = content.replace(old_school, new_school)

with open('app/db/models.py', 'w') as f:
    f.write(content)
