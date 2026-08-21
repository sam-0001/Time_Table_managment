import sys

def patch_file(file_path, old_str, new_str):
    with open(file_path, 'r') as f:
        content = f.read()
    content = content.replace(old_str, new_str)
    with open(file_path, 'w') as f:
        f.write(content)

# Teachers Create
old_t_create = """def create_teacher(
    teacher_in: TeacherCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    if not teacher_in.employee_id:"""

new_t_create = """def create_teacher(
    teacher_in: TeacherCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    if current_user.school.plan_type == "DEMO":
        if db.query(Teacher).filter(Teacher.school_id == current_user.school_id).count() >= 8:
            raise HTTPException(status_code=403, detail="Demo plan limited to 8 teachers. Upgrade to Pro to add more.")
    if not teacher_in.employee_id:"""
patch_file('app/api/routes/teachers.py', old_t_create, new_t_create)

# Note: Update and Delete for teachers is already patched by my previous sed commands!

# Classes Create
old_c_create = """def create_class(
    class_in: ClassCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    school_class = db.query(SchoolClass)"""
new_c_create = """def create_class(
    class_in: ClassCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    if current_user.school.plan_type == "DEMO":
        if db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == current_user.school_id).count() >= 4:
            raise HTTPException(status_code=403, detail="Demo plan limited to 4 classes. Upgrade to Pro to add more.")
    school_class = db.query(SchoolClass)"""
patch_file('app/api/routes/classes.py', old_c_create, new_c_create)

# Classes Update
old_c_up = """    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    school_class.name = class_in.name"""
new_c_up = """    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
    if getattr(school_class, "is_demo", False) and current_user.school.plan_type == "DEMO":
        raise HTTPException(status_code=403, detail="Cannot edit demo data. Upgrade to Pro.")
        
    school_class.name = class_in.name"""
patch_file('app/api/routes/classes.py', old_c_up, new_c_up)

# Classes Delete
old_c_del = """    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    db.delete(school_class)"""
new_c_del = """    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
    if getattr(school_class, "is_demo", False) and current_user.school.plan_type == "DEMO":
        raise HTTPException(status_code=403, detail="Cannot edit demo data. Upgrade to Pro.")
        
    db.delete(school_class)"""
patch_file('app/api/routes/classes.py', old_c_del, new_c_del)

# Subjects Create
old_s_create = """def create_subject(
    subject_in: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    if subject_in.class_id:"""
new_s_create = """def create_subject(
    subject_in: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    if current_user.school.plan_type == "DEMO":
        if db.query(Subject).join(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == current_user.school_id).count() >= 14:
            raise HTTPException(status_code=403, detail="Demo plan limited to 14 subjects. Upgrade to Pro to add more.")
    if subject_in.class_id:"""
patch_file('app/api/routes/subjects.py', old_s_create, new_s_create)

# Subjects Update
old_s_up = """    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    update_data = subject_in.model_dump(exclude_unset=True)"""
new_s_up = """    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if getattr(subject, "is_demo", False) and current_user.school.plan_type == "DEMO":
        raise HTTPException(status_code=403, detail="Cannot edit demo data. Upgrade to Pro.")
        
    update_data = subject_in.model_dump(exclude_unset=True)"""
patch_file('app/api/routes/subjects.py', old_s_up, new_s_up)

# Subjects Delete
old_s_del = """    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    db.delete(subject)"""
new_s_del = """    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if getattr(subject, "is_demo", False) and current_user.school.plan_type == "DEMO":
        raise HTTPException(status_code=403, detail="Cannot edit demo data. Upgrade to Pro.")
        
    db.delete(subject)"""
patch_file('app/api/routes/subjects.py', old_s_del, new_s_del)

