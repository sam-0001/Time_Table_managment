import os
import re

def insert_after(file_path, pattern, insertion):
    with open(file_path, 'r') as f:
        content = f.read()
    content = re.sub(pattern, lambda m: m.group(0) + insertion, content)
    with open(file_path, 'w') as f:
        f.write(content)

# Teachers
t_pattern = r'def create_teacher\(\n    teacher_in: TeacherCreate,\n    db: Session = Depends\(get_db\),\n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):'
t_insertion = """\n    if current_user.school.plan_type == "DEMO":\n        if db.query(Teacher).filter(Teacher.school_id == current_user.school_id).count() >= 8:\n            raise HTTPException(status_code=403, detail="Demo plan limited to 8 teachers. Please upgrade to Pro to add more.")"""
insert_after('app/api/routes/teachers.py', t_pattern, t_insertion)

t_update = r'def update_teacher\(\n    id: str,\n    teacher_in: TeacherUpdate,\n    db: Session = Depends\(get_db\),\n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):[\s\S]*?if not teacher:\n        raise HTTPException\(status_code=404, detail="Teacher not found"\)'
t_up_insertion = """\n    if teacher.is_demo and current_user.school.plan_type == "DEMO":\n        raise HTTPException(status_code=403, detail="Cannot edit demo data. Upgrade to Pro.")"""
insert_after('app/api/routes/teachers.py', t_update, t_up_insertion)

t_del = r'def delete_teacher\(\n    id: str,\n    db: Session = Depends\(get_db\),\n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):[\s\S]*?if not teacher:\n        raise HTTPException\(status_code=404, detail="Teacher not found"\)'
insert_after('app/api/routes/teachers.py', t_del, t_up_insertion)

# Classes
c_pattern = r'def create_class\(\n    class_in: ClassCreate, \n    db: Session = Depends\(get_db\), \n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):'
c_insertion = """\n    if current_user.school.plan_type == "DEMO":\n        if db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == current_user.school_id).count() >= 4:\n            raise HTTPException(status_code=403, detail="Demo plan limited to 4 classes. Please upgrade to Pro to add more.")"""
insert_after('app/api/routes/classes.py', c_pattern, c_insertion)

c_update = r'def update_class\(\n    class_id: str, \n    class_in: ClassCreate, \n    db: Session = Depends\(get_db\), \n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):[\s\S]*?if not school_class:\n        raise HTTPException\(status_code=404, detail="Class not found"\)'
c_up_insertion = """\n    if school_class.is_demo and current_user.school.plan_type == "DEMO":\n        raise HTTPException(status_code=403, detail="Cannot edit demo data. Upgrade to Pro.")"""
insert_after('app/api/routes/classes.py', c_update, c_up_insertion)

c_del = r'def delete_class\(\n    class_id: str, \n    db: Session = Depends\(get_db\), \n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):[\s\S]*?if not school_class:\n        raise HTTPException\(status_code=404, detail="Class not found"\)'
insert_after('app/api/routes/classes.py', c_del, c_up_insertion)

# Subjects
s_pattern = r'def create_subject\(\n    subject_in: SubjectCreate,\n    db: Session = Depends\(get_db\),\n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):'
s_insertion = """\n    if current_user.school.plan_type == "DEMO":\n        if db.query(Subject).join(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == current_user.school_id).count() >= 12:\n            raise HTTPException(status_code=403, detail="Demo plan limited to 12 subjects. Please upgrade to Pro to add more.")"""
insert_after('app/api/routes/subjects.py', s_pattern, s_insertion)

s_update = r'def update_subject\(\n    id: str,\n    subject_in: SubjectUpdate,\n    db: Session = Depends\(get_db\),\n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):[\s\S]*?if not subject:\n        raise HTTPException\(status_code=404, detail="Subject not found"\)'
s_up_insertion = """\n    if subject.is_demo and current_user.school.plan_type == "DEMO":\n        raise HTTPException(status_code=403, detail="Cannot edit demo data. Upgrade to Pro.")"""
insert_after('app/api/routes/subjects.py', s_update, s_up_insertion)

s_del = r'def delete_subject\(\n    id: str,\n    db: Session = Depends\(get_db\),\n    current_user: User = Depends\(require_roles\(\[RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN\]\)\)\n\):[\s\S]*?if not subject:\n        raise HTTPException\(status_code=404, detail="Subject not found"\)'
insert_after('app/api/routes/subjects.py', s_del, s_up_insertion)

