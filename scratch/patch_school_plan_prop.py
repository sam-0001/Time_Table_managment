import re

with open('app/db/models.py', 'r') as f:
    content = f.read()

content = content.replace(
    '    @property\n    def school_plan(self):\n        return self.school.plan_type if self.school else None',
    '    @property\n    def school_plan(self):\n        if self.is_demo_mode:\n            return "DEMO"\n        return self.school.plan_type if self.school else None'
)

with open('app/db/models.py', 'w') as f:
    f.write(content)
