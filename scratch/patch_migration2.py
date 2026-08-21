import sys

def patch():
    with open('scratch/migrate_to_new_school.py', 'r') as f:
        content = f.read()

    # Use UUID for teacher email to avoid unique constraint
    old = 'email=f"{t[2]}@teacher.com",'
    new = 'email=f"{t[2]}_{uuid.uuid4().hex[:6]}@teacher.com",'
    content = content.replace(old, new)

    with open('scratch/migrate_to_new_school.py', 'w') as f:
        f.write(content)

patch()
