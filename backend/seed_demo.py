from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import (
    School, SchoolSetting, AcademicYear, Teacher, SchoolClass, 
    Division, Subject, TeacherSubject, User, RoleEnum
)
from datetime import datetime, timedelta, time

def seed_demo_data():
    db: Session = SessionLocal()
    try:
        # Check if School exists
        school = db.query(School).first()
        if not school:
            school = School(
                name="Demo High School",
                code="DHS",
                address="123 Education Lane",
                city="Tech City",
                state="Innovation State",
                pincode="123456",
                email="admin@school.edu"
            )
            db.add(school)
            db.commit()
            db.refresh(school)
        
        # Check SchoolSettings
        setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == school.id).first()
        if not setting:
            setting = SchoolSetting(
                school_id=school.id,
                working_days=5,
                start_time=time(8, 0),
                end_time=time(14, 0),
                number_of_periods=7,
                period_duration=45,
                lunch_break_period=4
            )
            db.add(setting)
            db.commit()
        
        # Academic Year
        academic_year = db.query(AcademicYear).filter(AcademicYear.name == "temp-academic-year-id").first()
        if not academic_year:
            # We use "temp-academic-year-id" just so it matches the hardcoded string in the UI
            academic_year = AcademicYear(
                id="temp-academic-year-id",
                school_id=school.id,
                name="temp-academic-year-id",
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=365),
                is_active=True
            )
            db.add(academic_year)
            db.commit()
            db.refresh(academic_year)
        
        # Admin User
        admin_user = db.query(User).filter(User.email == "admin@school.edu").first()

        admin_user = db.query(User).filter(User.email == "admin@school.edu").first()

        # Build 3 Standards (8, 9, 10) with 2 Divisions each (A, B)
        classes_data = [
            ("8th Standard", 8),
            ("9th Standard", 9),
            ("10th Standard", 10)
        ]
        
        divisions_map = {}
        subjects_map = {}

        for c_name, c_level in classes_data:
            school_class = db.query(SchoolClass).filter(SchoolClass.name == c_name).first()
            if not school_class:
                school_class = SchoolClass(academic_year_id=academic_year.id, name=c_name, level=c_level)
                db.add(school_class)
                db.commit()
                db.refresh(school_class)
            
            # Create Subjects for this class
            subject_configs = [
                ("Mathematics", f"MATH{c_level}", 6),
                ("Science", f"SCI{c_level}", 6),
                ("English", f"ENG{c_level}", 6),
                ("Local Language", f"LANG{c_level}", 5),
                ("History", f"HIS{c_level}", 4),
                ("Geography", f"GEO{c_level}", 4),
                ("Physical Ed", f"PE{c_level}", 2),
                ("Art", f"ART{c_level}", 2)
            ]
            for s_name, s_code, periods in subject_configs:
                subject = db.query(Subject).filter(Subject.code == s_code).first()
                if not subject:
                    subject = Subject(class_id=school_class.id, name=s_name, code=s_code, weekly_periods=periods, double_period_allowed=False, is_lab=False)
                    db.add(subject)
                    db.commit()
                    db.refresh(subject)
                subjects_map[s_code] = subject

            # Create Divisions A and B
            for d_name in ["A", "B"]:
                div = db.query(Division).filter(Division.class_id == school_class.id, Division.name == d_name).first()
                if not div:
                    div = Division(class_id=school_class.id, name=d_name)
                    db.add(div)
                    db.commit()
                    db.refresh(div)
                divisions_map[f"{c_level}{d_name}"] = div

        # Create Teachers and assign them workloads
        teacher_configs = [
            ("T1", "Math Expert One", [("MATH8", "8A"), ("MATH8", "8B"), ("MATH9", "9A")], "8A"),
            ("T2", "Math Expert Two", [("MATH9", "9B"), ("MATH10", "10A"), ("MATH10", "10B")], "8B"),
            ("T3", "Science Expert One", [("SCI8", "8A"), ("SCI8", "8B"), ("SCI9", "9A")], "9A"),
            ("T4", "Science Expert Two", [("SCI9", "9B"), ("SCI10", "10A"), ("SCI10", "10B")], "9B"),
            ("T5", "English Expert One", [("ENG8", "8A"), ("ENG8", "8B"), ("ENG9", "9A")], "10A"),
            ("T6", "English Expert Two", [("ENG9", "9B"), ("ENG10", "10A"), ("ENG10", "10B")], "10B"),
            ("T7", "Lang/His One", [("LANG8", "8A"), ("LANG8", "8B"), ("LANG9", "9A"), ("HIS8", "8A"), ("HIS8", "8B"), ("HIS9", "9A")], None),
            ("T8", "Lang/His Two", [("LANG9", "9B"), ("LANG10", "10A"), ("LANG10", "10B"), ("HIS9", "9B"), ("HIS10", "10A"), ("HIS10", "10B")], None),
            ("T9", "Geo/Extra One", [("GEO8", "8A"), ("GEO8", "8B"), ("GEO9", "9A"), ("PE8", "8A"), ("PE8", "8B"), ("PE9", "9A"), ("ART8", "8A"), ("ART8", "8B"), ("ART9", "9A")], None),
            ("T10", "Geo/Extra Two", [("GEO9", "9B"), ("GEO10", "10A"), ("GEO10", "10B"), ("PE9", "9B"), ("PE10", "10A"), ("PE10", "10B"), ("ART9", "9B"), ("ART10", "10A"), ("ART10", "10B")], None),
        ]

        for t_emp_id, t_name, assignments, ct_div_key in teacher_configs:
            # Create user
            t_user = db.query(User).filter(User.email == f"{t_emp_id.lower()}@school.edu").first()
            if not t_user:
                from app.core.security import get_password_hash
                t_user = User(email=f"{t_emp_id.lower()}@school.edu", full_name=t_name, hashed_password=get_password_hash("password123"), role=RoleEnum.TEACHER)
                db.add(t_user)
                db.commit()
                db.refresh(t_user)

            # Create teacher profile
            teacher = db.query(Teacher).filter(Teacher.employee_id == t_emp_id).first()
            if not teacher:
                teacher = Teacher(user_id=t_user.id, employee_id=t_emp_id, max_daily_periods=7, max_weekly_periods=35, is_active=True)
                db.add(teacher)
                db.commit()
                db.refresh(teacher)

            # Assign Class Teacher
            if ct_div_key:
                div = divisions_map[ct_div_key]
                div.class_teacher_id = teacher.id
                db.add(div)
                db.commit()

            # Assign subjects
            for s_code, div_key in assignments:
                sub = subjects_map[s_code]
                div = divisions_map[div_key]
                ts = db.query(TeacherSubject).filter(TeacherSubject.teacher_id == teacher.id, TeacherSubject.subject_id == sub.id, TeacherSubject.division_id == div.id).first()
                if not ts:
                    ts = TeacherSubject(teacher_id=teacher.id, subject_id=sub.id, division_id=div.id)
                    db.add(ts)
            db.commit()

        print("Extremely Robust Demo data seeded successfully! 6 Divisions (8th, 9th, 10th) fully loaded.")
        
    except Exception as e:
        print(f"Error seeding demo data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
