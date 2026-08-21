import re

with open('app/db/models.py', 'r') as f:
    content = f.read()

user_prop = """    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"), nullable=True)

    @property
    def school_plan(self):
        return self.school.plan_type if self.school else None

    # Relationships"""

content = content.replace(
    '    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"), nullable=True)\n\n    # Relationships',
    user_prop
)

with open('app/db/models.py', 'w') as f:
    f.write(content)
