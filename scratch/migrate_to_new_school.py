import sys
import os
import uuid
sys.path.insert(0, os.path.abspath('.'))
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.db.models import *

sqlite_url = "sqlite:////Users/sohamchaudhari/Desktop/Time_Table/backend/sql_app.db"
postgres_url = "postgresql://postgres:TimeTable#1100@db.lxczvmpobvblymkuukim.supabase.co:5432/postgres"

sqlite_engine = create_engine(sqlite_url)
pg_engine = create_engine(postgres_url)

sqlite_db = Session(sqlite_engine)
pg_db = Session(pg_engine)

print("Starting migration...")

# Get the new user and school
new_user = pg_db.query(User).filter(User.email == "sc922467@gmail.com").first()
school_id = new_user.school_id
academic_year = pg_db.query(AcademicYear).filter(AcademicYear.school_id == school_id).first()
academic_year_id = academic_year.id

print(f"Migrating to School ID: {school_id}, Academic Year ID: {academic_year_id}")

# Update the School Settings to 6 days / 8 periods just like old sql_app.db
setting = pg_db.query(SchoolSetting).filter(SchoolSetting.school_id == school_id).first()
setting.working_days = 6
setting.number_of_periods = 8
setting.max_weekly_teacher_periods = 40
pg_db.commit()

# 1. Teachers
sqlite_teachers = sqlite_db.execute(text("SELECT t.id, u.full_name as name, t.employee_id, max_weekly_periods, max_daily_periods FROM teachers t JOIN users u ON t.user_id = u.id")).fetchall()
teacher_map = {} # sqlite_id -> pg_id
for t in sqlite_teachers:
    new_id = str(uuid.uuid4())
    teacher_map[t[0]] = new_id
    pg_teacher = Teacher(
        id=new_id,
        school_id=school_id,
        employee_id=t[2],
        max_weekly_periods=t[3],
        max_daily_periods=t[4],
        is_active=True
    )
    pg_db.add(pg_teacher)
    
    # Create User account for the teacher
    teacher_user = User(
        email=f"{t[2]}_{uuid.uuid4().hex[:6]}@teacher.com",
        hashed_password="placeholder",
        full_name=t[1],
        role=RoleEnum.TEACHER,
        school_id=school_id
    )
    pg_db.add(teacher_user)
    pg_db.flush()
    pg_teacher.user_id = teacher_user.id
pg_db.commit()
print(f"Migrated {len(teacher_map)} teachers.")

# 2. Classes and Divisions
sqlite_classes = sqlite_db.execute(text("SELECT id, name, level FROM classes")).fetchall()
class_map = {} # sqlite_id -> pg_id
for c in sqlite_classes:
    new_id = str(uuid.uuid4())
    class_map[c[0]] = new_id
    pg_class = SchoolClass(
        id=new_id,
        academic_year_id=academic_year_id,
        name=c[1],
        level=c[2]
    )
    pg_db.add(pg_class)
pg_db.commit()
print(f"Migrated {len(class_map)} classes.")

sqlite_divisions = sqlite_db.execute(text("SELECT id, class_id, name, class_teacher_id FROM divisions")).fetchall()
div_map = {} # sqlite_id -> pg_id
for d in sqlite_divisions:
    new_id = str(uuid.uuid4())
    div_map[d[0]] = new_id
    pg_div = Division(
        id=new_id,
        class_id=class_map[d[1]],
        name=d[2],
        class_teacher_id=teacher_map.get(d[3]) if d[3] else None
    )
    pg_db.add(pg_div)
pg_db.commit()
print(f"Migrated {len(div_map)} divisions.")

# 3. Subjects
sqlite_subjects = sqlite_db.execute(text("SELECT id, class_id, name, code, weekly_periods, is_lab, double_period_allowed FROM subjects")).fetchall()
subject_map = {} # sqlite_id -> pg_id
for s in sqlite_subjects:
    new_id = str(uuid.uuid4())
    subject_map[s[0]] = new_id
    pg_subject = Subject(
        id=new_id,
        class_id=class_map[s[1]],
        name=s[2],
        code=s[3],
        weekly_periods=s[4],
        is_lab=s[5],
        double_period_allowed=s[6]
    )
    pg_db.add(pg_subject)
pg_db.commit()
print(f"Migrated {len(subject_map)} subjects.")

# 4. Teacher Subjects
sqlite_ts = sqlite_db.execute(text("SELECT id, teacher_id, subject_id, division_id FROM teacher_subjects")).fetchall()
for ts in sqlite_ts:
    pg_ts = TeacherSubject(
        teacher_id=teacher_map[ts[1]],
        subject_id=subject_map[ts[2]],
        division_id=div_map[ts[3]]
    )
    pg_db.add(pg_ts)
pg_db.commit()
print(f"Migrated {len(sqlite_ts)} teacher-subject mappings.")

# 5. Timetable Slots (Optional, but let's migrate them if they exist)
sqlite_slots = sqlite_db.execute(text("SELECT id, division_id, subject_id, teacher_id, day_of_week, period_number FROM timetable_slots")).fetchall()
slot_map = {}
for slot in sqlite_slots:
    if slot[1] not in div_map or slot[2] not in subject_map or slot[3] not in teacher_map:
        continue
    new_id = str(uuid.uuid4())
    slot_map[slot[0]] = new_id
    pg_slot = TimetableSlot(
        id=new_id,
        division_id=div_map[slot[1]],
        subject_id=subject_map[slot[2]],
        teacher_id=teacher_map[slot[3]],
        day_of_week=slot[4],
        period_number=slot[5]
    )
    pg_db.add(pg_slot)
pg_db.commit()
print(f"Migrated {len(sqlite_slots)} timetable slots.")

# 6. Teacher Leaves & Substitutions
sqlite_leaves = sqlite_db.execute(text("SELECT id, teacher_id, date, leave_type, reason FROM teacher_leaves")).fetchall()
leave_map = {}
for leave in sqlite_leaves:
    new_id = str(uuid.uuid4())
    leave_map[leave[0]] = new_id
    pg_leave = TeacherLeave(
        id=new_id,
        teacher_id=teacher_map[leave[1]],
        date=leave[2],
        leave_type=leave[3],
        reason=leave[4]
    )
    pg_db.add(pg_leave)
pg_db.commit()

sqlite_subs = sqlite_db.execute(text("SELECT id, original_slot_id, substitute_teacher_id, date FROM substitutions")).fetchall()
for sub in sqlite_subs:
    if sub[1] in slot_map:
        pg_sub = Substitution(
            original_slot_id=slot_map[sub[1]],
            substitute_teacher_id=teacher_map[sub[2]],
            date=sub[3]
        )
        pg_db.add(pg_sub)
pg_db.commit()
print(f"Migrated leaves and substitutions.")

print("Migration completed successfully!")
