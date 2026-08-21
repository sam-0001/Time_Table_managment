import re

with open('app/api/routes/auth.py', 'r') as f:
    content = f.read()

content = content.replace(
    'from app.core.config import settings, create_access_token, create_refresh_token',
    'from app.core.security import create_refresh_token\nfrom app.core.config import settings'
)

with open('app/api/routes/auth.py', 'w') as f:
    f.write(content)
