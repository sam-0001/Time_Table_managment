import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.db.database import SessionLocal, Base, engine
from app.api.routes.teachers import create_teacher, TeacherCreate
from app.db.models import User

db = SessionLocal()

admin_user = db.query(User).filter_by(email="admin@test.com").first()

teacher_in = TeacherCreate(
    name="Test Teacher 2",
    email="test@teacher.com", # SAME EMAIL AS T001
    employee_id="T002",       # DIFFERENT ID
    mobile="1234567890",
    qualification="PhD",
    assignments=[],
    max_daily_periods=7,
    max_weekly_periods=32,
    class_teacher_of_division_id=None
)

try:
    res = create_teacher(teacher_in=teacher_in, db=db, current_user=admin_user)
    print("SUCCESS", res)
except Exception as e:
    import traceback
    traceback.print_exc()

