import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.db.database import SessionLocal
from app.db.models import SchoolSetting, Teacher, SchoolClass, Division, Subject, TeacherSubject

def check():
    db = SessionLocal()
    setting = db.query(SchoolSetting).first()

    print(f"--- SCHOOL SETTINGS ---")
    print(f"Working Days: {setting.working_days}")
    print(f"Periods/Day: {setting.number_of_periods}")
    if setting.weekly_schedule:
        max_school_periods = sum(day.get("periods", 0) for day in setting.weekly_schedule if day.get("is_working", True))
    else:
        max_school_periods = setting.working_days * setting.number_of_periods
    print(f"Total Periods Available Per Week: {max_school_periods}")
    print(f"Global Max Teacher Periods: {setting.max_weekly_teacher_periods}")
    print("\n--- DIVISION PERIOD CHECKS ---")

    divisions = db.query(Division).all()
    for d in divisions:
        ts_list = db.query(TeacherSubject).filter(TeacherSubject.division_id == d.id).all()
        req_periods = sum(ts.subject.weekly_periods for ts in ts_list)
        c_name = d.school_class.name if d.school_class else "Unknown"
        
        if req_periods > max_school_periods:
            print(f"WARNING: Division {c_name}-{d.name} requires {req_periods} periods, but only {max_school_periods} are available!")
        
        # Check subjects without teachers
        all_subjects = db.query(Subject).filter(Subject.class_id == d.class_id).all()
        assigned_subject_ids = [ts.subject_id for ts in ts_list]
        unassigned = [s.name for s in all_subjects if s.id not in assigned_subject_ids]
        if unassigned:
            print(f"INFO: Division {c_name}-{d.name} has subjects without any assigned teacher: {', '.join(unassigned)}")

    print("\n--- TEACHER WORKLOAD CHECKS ---")
    teachers = db.query(Teacher).filter(Teacher.is_active == True).all()
    for t in teachers:
        ts_list = db.query(TeacherSubject).filter(TeacherSubject.teacher_id == t.id).all()
        assigned_periods = sum(ts.subject.weekly_periods for ts in ts_list)
        t_name = t.user.full_name if t.user else t.employee_id
        
        if assigned_periods > t.max_weekly_periods:
            print(f"WARNING: Teacher {t_name} is assigned {assigned_periods} periods, exceeding their personal limit of {t.max_weekly_periods}!")
            
        if assigned_periods > setting.max_weekly_teacher_periods:
            print(f"WARNING: Teacher {t_name} is assigned {assigned_periods} periods, exceeding school limit of {setting.max_weekly_teacher_periods}!")

    print("\n--- CLASS TEACHER CHECKS ---")
    for d in divisions:
        if d.class_teacher_id:
            c_name = d.school_class.name if d.school_class else "Unknown"
            teaches = db.query(TeacherSubject).filter(
                TeacherSubject.division_id == d.id,
                TeacherSubject.teacher_id == d.class_teacher_id
            ).first()
            if not teaches:
                t = db.query(Teacher).filter(Teacher.id == d.class_teacher_id).first()
                t_name = t.user.full_name if (t and t.user) else t.employee_id if t else "Unknown"
                print(f"WARNING: Teacher {t_name} is the Class Teacher for {c_name}-{d.name}, but they don't teach any subjects to this class. This will crash the timetable engine which expects class teachers to take Period 1.")

if __name__ == "__main__":
    check()
