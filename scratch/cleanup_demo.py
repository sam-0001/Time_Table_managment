import os
os.environ["DATABASE_URL"] = "postgresql://postgres.lxczvmpobvblymkuukim:TimeTable%231100@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

from app.db.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    db.execute(text("DELETE FROM teacher_subjects WHERE teacher_id IN (SELECT id FROM teachers WHERE is_demo = TRUE)"))
    db.execute(text("DELETE FROM timetable_slots WHERE teacher_id IN (SELECT id FROM teachers WHERE is_demo = TRUE)"))
    db.execute(text("DELETE FROM teachers WHERE is_demo = TRUE"))
    db.execute(text("DELETE FROM subjects WHERE is_demo = TRUE"))
    db.execute(text("DELETE FROM divisions WHERE is_demo = TRUE"))
    db.execute(text("DELETE FROM classes WHERE is_demo = TRUE"))
    db.execute(text("DELETE FROM users WHERE is_demo = TRUE"))
    db.commit()
    print("Successfully deleted all demo data from all accounts!")
except Exception as e:
    db.rollback()
    print("Error deleting demo data:", e)

db.close()
