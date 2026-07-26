from app.db.database import SessionLocal
from app.api.routes.timetable import generate_timetable
from app.db.models import User

db = SessionLocal()
try:
    print(generate_timetable(academic_year_id="temp-academic-year-id", db=db, current_user=User()))
except Exception as e:
    print("Error:", e)
