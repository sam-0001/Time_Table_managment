import re

def insert_after(file_path, pattern, insertion):
    with open(file_path, 'r') as f:
        content = f.read()
    content = re.sub(pattern, lambda m: m.group(0) + insertion, content)
    with open(file_path, 'w') as f:
        f.write(content)

# Teachers
t_pattern = r'def create_teacher\(.*?current_user: User = Depends\(require_roles\(\[.*?\]\)\)\s*\):'
t_insertion = """\n    if current_user.school.plan_type == "DEMO":\n        if db.query(Teacher).filter(Teacher.school_id == current_user.school_id).count() >= 8:\n            raise HTTPException(status_code=403, detail="Demo plan limited to 8 teachers. Please upgrade to Pro to add more.")"""
insert_after('app/api/routes/teachers.py', t_pattern, t_insertion)

# It's easier to just do it precisely using python's AST or simple string replacing where we know it matches.
