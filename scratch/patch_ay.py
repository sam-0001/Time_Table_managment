import os
import re

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Add the helper
    if "def resolve_academic_year" not in content:
        helper = """
def resolve_academic_year(db: Session, current_user, requested_id: str) -> str:
    if requested_id == "temp-academic-year-id" or not requested_id:
        from app.db.models import AcademicYear
        ay = db.query(AcademicYear).filter(AcademicYear.school_id == current_user.school_id, AcademicYear.is_active == True).first()
        if ay: return ay.id
    return requested_id
"""
        content = content.replace("router = APIRouter()\n", "router = APIRouter()\n" + helper)

    # Patch classes.py
    if "classes.py" in filepath:
        content = content.replace(
            "class_in.academic_year_id",
            "resolve_academic_year(db, current_user, class_in.academic_year_id)"
        )
        content = content.replace(
            "if academic_year_id:",
            "academic_year_id = resolve_academic_year(db, current_user, academic_year_id)\n    if academic_year_id:"
        )

    # Patch timetable.py
    if "timetable.py" in filepath:
        content = content.replace(
            "def generate_timetable(\n    academic_year_id: str,",
            "def generate_timetable(\n    academic_year_id: str,"
        )
        # We need to replace all uses of academic_year_id with resolved one
        # Actually it's easier to just do it at the start of the function body
        content = content.replace(
            "school_setting = db.query(SchoolSetting)",
            "academic_year_id = resolve_academic_year(db, current_user, academic_year_id)\n    school_setting = db.query(SchoolSetting)"
        )
        content = content.replace(
            "slots = db.query(TimetableSlot)",
            "academic_year_id = resolve_academic_year(db, current_user, academic_year_id)\n    slots = db.query(TimetableSlot)"
        )

    with open(filepath, 'w') as f:
        f.write(content)

patch_file("app/api/routes/classes.py")
patch_file("app/api/routes/timetable.py")
