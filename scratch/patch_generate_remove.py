import sys

def patch():
    with open('app/api/routes/timetable.py', 'r') as f:
        content = f.read()

    old_gen = """def generate_timetable(
    academic_year_id: str = Query(..., description="ID of the academic year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    if current_user.school.plan_type == "DEMO":
        raise HTTPException(status_code=402, detail="Payment Required. Please upgrade to Pro to generate a real timetable!")"""

    new_gen = """def generate_timetable(
    academic_year_id: str = Query(..., description="ID of the academic year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):"""
    
    content = content.replace(old_gen, new_gen)
    with open('app/api/routes/timetable.py', 'w') as f:
        f.write(content)
patch()
