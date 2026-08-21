import sys

def patch():
    with open('app/api/routes/timetable.py', 'r') as f:
        content = f.read()

    old_gen = """def generate_timetable(
    academic_year_id: str = Query(..., description="ID of the academic year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    school_setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == current_user.school_id).first()"""

    new_gen = """def generate_timetable(
    academic_year_id: str = Query(..., description="ID of the academic year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    if current_user.school.plan_type == "PRO" and current_user.school.available_generations <= 0:
        raise HTTPException(status_code=402, detail="You have used all your generations. Please purchase more.")
        
    school_setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == current_user.school_id).first()"""
    
    content = content.replace(old_gen, new_gen)
    
    # Also need to deduct the credit on success
    old_success = """            return {"status": "SUCCESS", "timetable": timetable}
        else:
            return {"status": "FAILED","""
            
    new_success = """            if current_user.school.plan_type == "PRO" and current_user.school.available_generations < 999999:
                current_user.school.available_generations -= 1
                db.commit()
            return {"status": "SUCCESS", "timetable": timetable}
        else:
            return {"status": "FAILED","""
            
    content = content.replace(old_success, new_success)
    
    with open('app/api/routes/timetable.py', 'w') as f:
        f.write(content)

patch()
