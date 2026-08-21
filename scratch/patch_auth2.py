import sys

def patch():
    with open('app/api/routes/auth.py', 'r') as f:
        content = f.read()

    old_setting = """    settings = SchoolSetting(school_id=school.id)
    db.add(settings)"""

    new_setting = """    settings = SchoolSetting(
        school_id=school.id,
        working_days=6 if plan == "DEMO" else 5,
        number_of_periods=8 if plan == "DEMO" else 7,
        max_weekly_teacher_periods=48 if plan == "DEMO" else 32
    )
    db.add(settings)"""
    
    content = content.replace(old_setting, new_setting)
    with open('app/api/routes/auth.py', 'w') as f:
        f.write(content)
patch()
