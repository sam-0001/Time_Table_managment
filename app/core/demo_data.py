import uuid
from sqlalchemy.orm import Session
from app.db.models import SchoolClass, Division, Subject, Teacher, TeacherSubject, User, RoleEnum

def generate_demo_data(db: Session, school_id: str, academic_year_id: str):
    # Classes & Divisions
    classes = []
    divisions = []
    
    for lvl, name in [(9, "9th"), (10, "10th")]:
        cls = SchoolClass(
            id=str(uuid.uuid4()),
            academic_year_id=academic_year_id,
            name=name,
            level=lvl,
            is_demo=True
        )
        classes.append(cls)
        db.add(cls)
        
        for div_name in ["A", "B"]:
            div = Division(
                id=str(uuid.uuid4()),
                class_id=cls.id,
                name=div_name,
                is_demo=True
            )
            divisions.append(div)
            db.add(div)
    db.flush()

    # Subjects & Teachers
    subject_names = ["Mathematics", "Science", "English", "History", "Geography", "Physical Education"]
    subject_codes = ["MATH", "SCI", "ENG", "HIS", "GEO", "PE"]
    
    for i in range(6):
        subj_name = subject_names[i]
        subj_code = subject_codes[i]
        
        # Teacher
        t_id = str(uuid.uuid4())
        teacher = Teacher(
            id=t_id,
            school_id=school_id,
            employee_id=f"DEMO-{subj_code}-{school_id[:8]}",
            max_daily_periods=8,
            max_weekly_periods=40,
            is_active=True,
            is_demo=True
        )
        db.add(teacher)
        
        user = User(
            id=str(uuid.uuid4()),
            email=f"demo_{subj_code.lower()}_{school_id[:8]}@demo.com",
            hashed_password="demo",
            full_name=f"Demo {subj_name} Teacher",
            role=RoleEnum.TEACHER,
            school_id=school_id
        )
        db.add(user)
        db.flush()
        teacher.user_id = user.id
        
        # Subjects per class
        for cls in classes:
            subj = Subject(
                id=str(uuid.uuid4()),
                class_id=cls.id,
                name=subj_name,
                code=subj_code,
                weekly_periods=8, # 6 subjects * 8 periods = 48
                is_demo=True
            )
            db.add(subj)
            db.flush()
            
            # Map teacher to all divisions of this class
            for div in [d for d in divisions if d.class_id == cls.id]:
                ts = TeacherSubject(
                    id=str(uuid.uuid4()),
                    teacher_id=teacher.id,
                    subject_id=subj.id,
                    division_id=div.id
                )
                db.add(ts)

    db.commit()
