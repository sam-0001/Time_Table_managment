import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.db.database import SessionLocal
from app.db.models import TeacherSubject

db = SessionLocal()

ts_db = db.query(TeacherSubject).filter_by(teacher_id='9e00ccd8-4f5e-41c7-913c-9f61299f2fc3', division_id='75ca5b1f-519c-4a9c-bdc9-855a2d9b1b7c').all()
total = sum([ts.subject.weekly_periods for ts in ts_db])
print("Teacher 9e00ccd8... teaches division 75ca... for", total, "periods")
