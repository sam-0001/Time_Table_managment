import sys

def patch():
    with open('app/db/models.py', 'r') as f:
        content = f.read()

    # SchoolClass
    old = 'level = Column(Integer, nullable=False) # for sorting'
    new = 'level = Column(Integer, nullable=False) # for sorting\n    is_demo = Column(Boolean, default=False)'
    content = content.replace(old, new)
    
    # Division
    old = 'classroom_id = Column(String, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True)'
    new = 'classroom_id = Column(String, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True)\n    is_demo = Column(Boolean, default=False)'
    content = content.replace(old, new)
    
    # Subject
    old = 'double_period_allowed = Column(Boolean, default=False)'
    new = 'double_period_allowed = Column(Boolean, default=False)\n    is_demo = Column(Boolean, default=False)'
    content = content.replace(old, new)

    # School
    old = 'name = Column(String, index=True)'
    new = 'name = Column(String, index=True)\n    plan_type = Column(String, default="DEMO")'
    content = content.replace(old, new)

    with open('app/db/models.py', 'w') as f:
        f.write(content)

patch()
