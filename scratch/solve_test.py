import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.db.database import SessionLocal
from app.db.models import Teacher, SchoolClass, Division, Subject, TeacherSubject, SchoolSetting
from app.services.timetable_engine import TimetableGenerator

db = SessionLocal()

school_setting = db.query(SchoolSetting).first()
academic_year_id = db.query(SchoolClass).first().academic_year_id

teachers_db = db.query(Teacher).filter(Teacher.is_active == True).all()
teachers = [
    {
        "id": t.id,
        "max_weekly": t.max_weekly_periods,
        "max_daily": t.max_daily_periods,
        "is_class_teacher_of": t.class_teacher_of.id if t.class_teacher_of else None
    }
    for t in teachers_db
]

classes_db = db.query(SchoolClass).filter(SchoolClass.academic_year_id == academic_year_id).all()
class_ids = [c.id for c in classes_db]
classes = [{"id": c.id, "name": c.name} for c in classes_db]

divisions_db = db.query(Division).join(SchoolClass).filter(SchoolClass.academic_year_id == academic_year_id).all()
divisions = [{"id": d.id, "class_id": d.class_id} for d in divisions_db]

subjects_db = db.query(Subject).filter(Subject.class_id.in_(class_ids)).all()
subjects = [{"id": s.id, "is_lab": s.is_lab, "double_period_allowed": s.double_period_allowed} for s in subjects_db]

ts_db = db.query(TeacherSubject).join(Subject).filter(Subject.class_id.in_(class_ids)).all()
teacher_subjects = []
for ts in ts_db:
    teacher_subjects.append({
        "teacher_id": ts.teacher_id,
        "subject_id": ts.subject_id,
        "division_id": ts.division_id,
        "weekly_periods": ts.subject.weekly_periods
    })

generator = TimetableGenerator(
    teachers=teachers,
    classes=classes,
    divisions=divisions,
    subjects=subjects,
    teacher_subjects=teacher_subjects,
    days=school_setting.working_days,
    periods_per_day=school_setting.number_of_periods,
    lunch_break_period=school_setting.lunch_break_period,
    weekly_schedule=school_setting.weekly_schedule,
    global_max_weekly_teacher_periods=school_setting.max_weekly_teacher_periods
)

res = generator.generate()
print(res["status"])
if res["status"] != "SUCCESS":
    print(res["reason"])
