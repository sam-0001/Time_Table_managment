import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from app.db.database import SessionLocal, Base, engine
from app.api.routes.teachers import create_teacher, TeacherCreate
from app.db.models import User

db = SessionLocal()
Base.metadata.create_all(engine)

from app.db.models import RoleEnum
admin_user = db.query(User).filter_by(email="admin@test.com").first()
if not admin_user:
    admin_user = User(email="admin@test.com", full_name="Admin", hashed_password="pw", role=RoleEnum.SUPER_ADMIN)
    db.add(admin_user)
    db.commit()

teacher_in = TeacherCreate(
    name="Test Teacher",
    email="test@teacher.com",
    employee_id="T001",
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

