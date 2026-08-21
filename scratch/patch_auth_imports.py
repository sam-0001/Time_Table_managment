import re

with open('app/api/routes/auth.py', 'r') as f:
    content = f.read()

content = content.replace(
    'from app.core.security import verify_password, get_password_hash',
    'from app.core.security import verify_password, get_password_hash, create_access_token\nfrom app.core.config import settings'
)
content = content.replace(
    'security.create_access_token(',
    'create_access_token('
)

with open('app/api/routes/auth.py', 'w') as f:
    f.write(content)
