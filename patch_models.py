import re

with open("app/db/models.py", "r") as f:
    content = f.read()

# Add to RoleEnum
content = content.replace(
    'TEACHER = "TEACHER"',
    'TEACHER = "TEACHER"\n    STUDENT = "STUDENT"\n    PARENT = "PARENT"'
)

# Add relation to Division
content = content.replace(
    'slots = relationship("TimetableSlot", back_populates="division", cascade="all, delete-orphan")',
    'slots = relationship("TimetableSlot", back_populates="division", cascade="all, delete-orphan")\n    students = relationship("Student", back_populates="division")'
)

# Append Student and Parent models
models_to_add = """

class Parent(Base):
    __tablename__ = "parents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"))
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    
    user = relationship("User")
    school = relationship("School")
    students = relationship("Student", back_populates="parent")

class Student(Base):
    __tablename__ = "students"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"))
    parent_id = Column(String, ForeignKey("parents.id", ondelete="SET NULL"), nullable=True)
    division_id = Column(String, ForeignKey("divisions.id", ondelete="SET NULL"), nullable=True)
    
    admission_number = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    blood_group = Column(String, nullable=True)
    address = Column(String, nullable=True)
    
    user = relationship("User")
    school = relationship("School")
    parent = relationship("Parent", back_populates="students")
    division = relationship("Division", back_populates="students")
"""

content += models_to_add

with open("app/db/models.py", "w") as f:
    f.write(content)
