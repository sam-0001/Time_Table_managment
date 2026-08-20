import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.db.database import SessionLocal
from app.db.models import Teacher, SchoolClass, Division, Subject, TeacherSubject, SchoolSetting
from ortools.sat.python import cp_model

db = SessionLocal()

school_setting = db.query(SchoolSetting).first()
academic_year_id = db.query(SchoolClass).first().academic_year_id

ts_db = db.query(TeacherSubject).join(Subject).all()
teacher_subjects = []
for ts in ts_db:
    teacher_subjects.append({
        "teacher_id": ts.teacher_id, "subject_id": ts.subject_id, "division_id": ts.division_id, "weekly_periods": ts.subject.weekly_periods
    })

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

model = cp_model.CpModel()
assignments = {}
for ts in teacher_subjects:
    t = ts["teacher_id"]
    d = ts["division_id"]
    s = ts["subject_id"]
    for day, p in schedule_config:
        assignments[(t, d, s, day, p)] = model.NewBoolVar(f"a_{t}_{d}_{s}_{day}_{p}")

# C1
for ts in teacher_subjects:
    t, d, s, req = ts["teacher_id"], ts["division_id"], ts["subject_id"], ts["weekly_periods"]
    model.Add(sum(assignments[(t, d, s, day, p)] for day, p in schedule_config) == req)

# C2
for t in {ts["teacher_id"] for ts in teacher_subjects}:
    for day, p in schedule_config:
        model.Add(sum(assignments[(ts["teacher_id"], ts["division_id"], ts["subject_id"], day, p)] for ts in teacher_subjects if ts["teacher_id"] == t) <= 1)

# C3
for d in {ts["division_id"] for ts in teacher_subjects}:
    for day, p in schedule_config:
        model.Add(sum(assignments[(ts["teacher_id"], ts["division_id"], ts["subject_id"], day, p)] for ts in teacher_subjects if ts["division_id"] == d) <= 1)

solver = cp_model.CpSolver()
status = solver.Solve(model)
print("Minimal Status:", status)
