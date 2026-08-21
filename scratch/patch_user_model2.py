import re

with open('app/db/models.py', 'r') as f:
    content = f.read()

user_prop = """    @property
    def school_plan(self):
        return self.school.plan_type if self.school else None
        
    _is_demo_mode = False
    
    @property
    def is_demo_mode(self):
        return getattr(self, "_is_demo_mode", False)
        
    @is_demo_mode.setter
    def is_demo_mode(self, value):
        self._is_demo_mode = value"""

content = content.replace(
    '    @property\n    def school_plan(self):\n        return self.school.plan_type if self.school else None',
    user_prop
)

with open('app/db/models.py', 'w') as f:
    f.write(content)
