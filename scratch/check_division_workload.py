import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import TeacherSubject, Subject, Division

postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"
engine = create_engine(postgres_url)
db = Session(engine)

ts_db = db.query(TeacherSubject).join(Subject).all()
workloads = {}
for ts in ts_db:
    did = ts.division_id
    periods = ts.subject.weekly_periods
    if did not in workloads:
        workloads[did] = 0
    workloads[did] += periods

for did, w in workloads.items():
    div = db.query(Division).get(did)
    cls = div.school_class.name
    print(f"Division {cls}-{div.name} total workload: {w}")

