def patch():
    with open('app/api/routes/auth.py', 'r') as f:
        content = f.read()

    old = "working_days=6 if plan == \"DEMO\" else 5,\n        number_of_periods=8 if plan == \"DEMO\" else 7,\n        max_weekly_teacher_periods=48 if plan == \"DEMO\" else 32"
    new = "working_days=6 if school.plan_type == \"DEMO\" else 5,\n        number_of_periods=8 if school.plan_type == \"DEMO\" else 7,\n        max_weekly_teacher_periods=48 if school.plan_type == \"DEMO\" else 32"
    
    if old in content:
        content = content.replace(old, new)
        with open('app/api/routes/auth.py', 'w') as f:
            f.write(content)
        print("Patched successfully")
    else:
        print("Could not find the string to replace")

patch()
