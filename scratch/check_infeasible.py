import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.db.database import SessionLocal
from app.db.models import Teacher, SchoolClass, Division, Subject, TeacherSubject, SchoolSetting

db = SessionLocal()

school_setting = db.query(SchoolSetting).first()
if not school_setting:
    print("No school setting")
    sys.exit()

print("Working days:", school_setting.working_days)
print("Periods per day:", school_setting.number_of_periods)
print("Weekly schedule:", school_setting.weekly_schedule)

ts_db = db.query(TeacherSubject).all()
div_reqs = {}
teacher_reqs = {}
for ts in ts_db:
    req = ts.subject.weekly_periods
    div_reqs[ts.division_id] = div_reqs.get(ts.division_id, 0) + req
    teacher_reqs[ts.teacher_id] = teacher_reqs.get(ts.teacher_id, 0) + req

print("Division required periods:")
for k, v in div_reqs.items():
    print(k, v)
    
print("Teacher required periods:")
for k, v in teacher_reqs.items():
    print(k, v)

# Check schedule config
schedule_config = []
if school_setting.weekly_schedule:
    for day_conf in school_setting.weekly_schedule:
        if not day_conf.get("is_working", True): continue
        for p in range(day_conf["periods"]):
            schedule_config.append((day_conf["day"], p))
else:
    for day_index in range(school_setting.working_days):
        for p in range(school_setting.number_of_periods):
            schedule_config.append((day_index, p))
            
print("Total slots available per division:", len(schedule_config))

for t in db.query(Teacher).filter(Teacher.is_active == True).all():
    print(f"Teacher {t.id} max_daily: {t.max_daily_periods}, max_weekly: {t.max_weekly_periods}, is_ct: {t.class_teacher_of.id if t.class_teacher_of else None}")

