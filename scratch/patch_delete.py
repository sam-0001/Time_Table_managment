import sys

def patch():
    with open('app/api/routes/timetable.py', 'r') as f:
        content = f.read()

    old_delete = """        # Clear old slots for this academic year
        db.query(TimetableSlot).join(Teacher).filter(Teacher.school_id == current_user.school_id, 
            TimetableSlot.division_id.in_([d["id"] for d in divisions])
        ).delete(synchronize_session=False)"""

    new_delete = """        # Clear old slots for this academic year
        teacher_ids = [t.id for t in db.query(Teacher.id).filter(Teacher.school_id == current_user.school_id).all()]
        db.query(TimetableSlot).filter(
            TimetableSlot.teacher_id.in_(teacher_ids),
            TimetableSlot.division_id.in_([d["id"] for d in divisions])
        ).delete(synchronize_session=False)"""

    content = content.replace(old_delete, new_delete)

    with open('app/api/routes/timetable.py', 'w') as f:
        f.write(content)

patch()
