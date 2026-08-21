import re

with open('app/api/deps.py', 'r') as f:
    content = f.read()

new_deps = """    if is_demo_mode and token_school_id:
        from app.db.models import School
        demo_school = db.query(School).filter(School.id == token_school_id).first()
        db.expunge(user)
        user.__dict__['school'] = demo_school
        user.real_school_id = user.school_id
        user.school_id = token_school_id
        user.is_demo_mode = True
    else:"""

content = content.replace(
    '    if is_demo_mode and token_school_id:\n        from app.db.models import School\n        demo_school = db.query(School).filter(School.id == token_school_id).first()\n        user.school = demo_school\n        db.expunge(user)\n        user.real_school_id = user.school_id\n        user.school_id = token_school_id\n        user.is_demo_mode = True\n    else:',
    new_deps
)

with open('app/api/deps.py', 'w') as f:
    f.write(content)
