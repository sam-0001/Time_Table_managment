import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models import Subject
import uuid

def copy_subjects():
    db = SessionLocal()
    
    class_9_id = 'aec1981e-eac0-46f4-8bf9-44dd2d67976f'
    class_10_id = 'b7e81091-a8e6-45d1-af27-f71447794473'
    
    subjects_9 = db.query(Subject).filter(Subject.class_id == class_9_id).all()
    
    if not subjects_9:
        print("No subjects found in 9th.")
        return

    subjects_10_existing = db.query(Subject).filter(Subject.class_id == class_10_id).all()
    existing_codes = {s.code for s in subjects_10_existing}
    
    added = 0
    for s in subjects_9:
        if s.code not in existing_codes:
            new_subject = Subject(
                id=str(uuid.uuid4()),
                class_id=class_10_id,
                name=s.name,
                code=s.code,
                weekly_periods=s.weekly_periods,
                double_period_allowed=s.double_period_allowed,
                is_lab=s.is_lab
            )
            db.add(new_subject)
            added += 1
            
    db.commit()
    print(f"Successfully added {added} subjects to 10th class.")

if __name__ == "__main__":
    copy_subjects()
