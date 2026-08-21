import re

with open('frontend/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

content = content.replace("res =>", "(res: any) =>")

with open('frontend/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
