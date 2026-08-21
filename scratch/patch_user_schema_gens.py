import re

with open('app/schemas/user.py', 'r') as f:
    content = f.read()

content = content.replace(
    'is_demo_mode: Optional[bool] = False',
    'is_demo_mode: Optional[bool] = False\n    available_generations: Optional[int] = 0'
)

with open('app/schemas/user.py', 'w') as f:
    f.write(content)

with open('app/db/models.py', 'r') as f:
    content = f.read()

user_prop = """    @property
    def school_plan(self):
        if self.is_demo_mode:
            return "DEMO"
        return self.school.plan_type if self.school else None

    @property
    def available_generations(self):
        return self.school.available_generations if self.school else 0"""

content = content.replace(
    '    @property\n    def school_plan(self):\n        if self.is_demo_mode:\n            return "DEMO"\n        return self.school.plan_type if self.school else None',
    user_prop
)

with open('app/db/models.py', 'w') as f:
    f.write(content)
