import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.db.database import SessionLocal
from app.db.models import SchoolSetting, Teacher, SchoolClass, Division, Subject, TeacherSubject
from app.services.timetable_engine import TimetableGenerator

db = SessionLocal()
academic_year_id = "temp-academic-year-id"
school_setting = db.query(SchoolSetting).first()

classes_db = db.query(SchoolClass).filter(SchoolClass.academic_year_id == academic_year_id).all()
class_ids = [c.id for c in classes_db]

ts_db = db.query(TeacherSubject).join(Subject).filter(Subject.class_id.in_(class_ids)).all()

division_reqs = {}
for ts in ts_db:
    d = ts.division_id
    if d not in division_reqs:
        division_reqs[d] = 0
    division_reqs[d] += ts.subject.weekly_periods

for d, req in division_reqs.items():
    print(f"Division {d}: requires {req} periods")
    
available_periods = school_setting.working_days * school_setting.number_of_periods
print(f"Available periods per week: {available_periods}")
