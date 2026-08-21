import re

with open('app/api/routes/auth.py', 'r') as f:
    content = f.read()

demo_routes = """
@router.post("/enter-demo")
def enter_demo(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if they already have a demo school
    demo_school_name = f"Demo_{current_user.id}"
    demo_school = db.query(School).filter(School.name == demo_school_name).first()
    
    if not demo_school:
        demo_school = School(name=demo_school_name, plan_type="DEMO")
        db.add(demo_school)
        db.commit()
        db.refresh(demo_school)
        
        settings = SchoolSetting(
            school_id=demo_school.id,
            working_days=6,
            number_of_periods=8,
            max_weekly_teacher_periods=48
        )
        db.add(settings)
        
        current_year = datetime.now().year
        academic_year = AcademicYear(
            school_id=demo_school.id,
            name=f"{current_year}-{current_year+1}",
            start_date=datetime(current_year, 4, 1),
            end_date=datetime(current_year+1, 3, 31),
            is_active=True
        )
        db.add(academic_year)
        db.commit()
        db.refresh(academic_year)
        
        from app.core.demo_data import generate_demo_data
        generate_demo_data(db, demo_school.id, academic_year.id)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={
            "sub": current_user.id, 
            "role": current_user.role.value,
            "school_id": demo_school.id,
            "is_demo_mode": True,
            "real_school_id": current_user.school_id
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_demo_mode": True}

@router.post("/exit-demo")
def exit_demo(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # They want to go back to their real school
    # The real school id is passed via token override in get_current_user
    real_school_id = getattr(current_user, "real_school_id", current_user.school_id)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={
            "sub": current_user.id, 
            "role": current_user.role.value
            # no school_id override needed for real school
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_demo_mode": False}
"""

if "/enter-demo" not in content:
    content += demo_routes
    with open('app/api/routes/auth.py', 'w') as f:
        f.write(content)
