import re

with open('frontend/src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'if (error.response?.status === 402) {',
    'if (error.response?.status === 402 || error.response?.status === 403) {'
)

with open('frontend/src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)
