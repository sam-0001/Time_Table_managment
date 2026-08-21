import os
os.environ["DATABASE_URL"] = "postgresql://postgres.lxczvmpobvblymkuukim:TimeTable%231100@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

from app.db.database import SessionLocal
from app.db.models import User, AcademicYear
from app.core.demo_data import generate_demo_data

db = SessionLocal()

user = db.query(User).filter(User.email == "sam000123456789001@gmail.com").first()
if user:
    ay = db.query(AcademicYear).filter(AcademicYear.school_id == user.school_id).first()
    if ay:
        print("Found User and Academic Year. Generating demo data...")
        try:
            generate_demo_data(db, user.school_id, ay.id)
            print("Successfully injected demo data!")
        except Exception as e:
            print("Error injecting:", e)
    else:
        print("No Academic Year found for this user's school!")
else:
    print("User not found!")

db.close()
