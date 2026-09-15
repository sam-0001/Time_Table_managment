from app.db.database import SessionLocal
from app.db.models import Teacher

db = SessionLocal()
teachers = db.query(Teacher).all()
count = 0
for t in teachers:
    updated = False
    if t.mobile == "nan" or t.mobile == "NaN":
        t.mobile = ""
        updated = True
    if t.qualification == "nan" or t.qualification == "NaN":
        t.qualification = ""
        updated = True
    if updated:
        count += 1
db.commit()
print(f"Fixed {count} teachers with 'nan' data")
