import re

with open('app/api/routes/timetable.py', 'r') as f:
    content = f.read()

new_logic = """    academic_year_id = resolve_academic_year(db, current_user, academic_year_id)
    
    if current_user.school.plan_type != "DEMO":
        if current_user.school.available_generations <= 0 and current_user.email != "sc922467@gmail.com":
            raise HTTPException(status_code=403, detail="No generations left. Please buy more credits.")
            
    school_setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == current_user.school_id).first()"""

content = content.replace(
    '    academic_year_id = resolve_academic_year(db, current_user, academic_year_id)\n    school_setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == current_user.school_id).first()',
    new_logic
)

success_logic = """    if result["status"] == "SUCCESS":
        if current_user.school.plan_type != "DEMO" and current_user.email != "sc922467@gmail.com":
            current_user.school.available_generations -= 1
            
        # Clear old slots for this academic year"""

content = content.replace(
    '    if result["status"] == "SUCCESS":\n        # Clear old slots for this academic year',
    success_logic
)

with open('app/api/routes/timetable.py', 'w') as f:
    f.write(content)
