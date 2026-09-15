import re

with open("app/db/models.py", "r") as f:
    content = f.read()

models_to_add = """

class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"))
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"))
    division_id = Column(String, ForeignKey("divisions.id", ondelete="CASCADE"))
    recorded_by_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    date = Column(DateTime, nullable=False)
    status = Column(String, default="PRESENT") # PRESENT, ABSENT, LATE, HALF_DAY
    remarks = Column(String, nullable=True)
    
    student = relationship("Student")
    division = relationship("Division")
    recorded_by = relationship("User")
"""

content += models_to_add

with open("app/db/models.py", "w") as f:
    f.write(content)
