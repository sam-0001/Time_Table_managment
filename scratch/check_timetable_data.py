import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import SchoolSetting, Teacher, SchoolClass, Division, Subject, TeacherSubject, User

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

user = db.query(User).filter(User.email == "admin@school.edu").first()
print(f"School ID: {user.school_id}")

setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == user.school_id).first()
if not setting:
    print("NO SETTING FOUND!")
else:
    print(f"Settings: working_days={setting.working_days}, periods={setting.number_of_periods}")

classes = db.query(SchoolClass).filter(SchoolClass.academic_year_id == 'temp-academic-year-id').all()
print(f"Classes: {len(classes)}")

ts_db = db.query(TeacherSubject).join(Subject).filter(Subject.class_id.in_([c.id for c in classes])).all()
print(f"Teacher Subjects: {len(ts_db)}")

# Print some of them
for ts in ts_db[:5]:
    print(f"Teacher {ts.teacher_id} -> Subject {ts.subject.name} ({ts.subject.weekly_periods} periods)")
