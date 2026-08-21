import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import TeacherSubject, Subject, User

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

ts_db = db.query(TeacherSubject).join(Subject).all()
workloads = {}
for ts in ts_db:
    tid = ts.teacher_id
    periods = ts.subject.weekly_periods
    if tid not in workloads:
        workloads[tid] = 0
    workloads[tid] += periods

for tid, w in workloads.items():
    print(f"Teacher {tid} total workload: {w}")

