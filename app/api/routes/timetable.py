from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.database import get_db
from app.db.models import User, RoleEnum, Teacher, SchoolClass, Division, Subject, TeacherSubject, TimetableSlot, SchoolSetting
from app.api.deps import get_current_user, require_roles
from app.services.timetable_engine import TimetableGenerator

router = APIRouter()

def resolve_academic_year(db: Session, current_user, requested_id: str) -> str:
    if requested_id == "temp-academic-year-id" or not requested_id:
        from app.db.models import AcademicYear
        ay = db.query(AcademicYear).filter(AcademicYear.school_id == current_user.school_id, AcademicYear.is_active == True).first()
        if ay: return ay.id
    return requested_id

@router.post("/generate", status_code=status.HTTP_200_OK)
def generate_timetable(
    academic_year_id: str,
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL, RoleEnum.TIMETABLE_COORDINATOR]))
):
    # 1. Fetch constraints and data
    academic_year_id = resolve_academic_year(db, current_user, academic_year_id)
    
    if current_user.school.plan_type != "DEMO":
        if current_user.school.available_generations <= 0 and current_user.email != "sc922467@gmail.com":
            raise HTTPException(status_code=403, detail="No generations left. Please buy more credits.")
            
    school_setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == current_user.school_id).first()
    if not school_setting:
        raise HTTPException(status_code=400, detail="School settings not found")
        
    teachers_db = db.query(Teacher).filter(Teacher.school_id == current_user.school_id, Teacher.is_active == True).all()
    teachers = [
        {
            "id": t.id,
            "max_weekly": t.max_weekly_periods,
            "max_daily": t.max_daily_periods,
            "is_class_teacher_of": t.class_teacher_of.id if t.class_teacher_of else None
        }
        for t in teachers_db
    ]
    
    classes_db = db.query(SchoolClass).filter(SchoolClass.academic_year_id == academic_year_id).all()
    class_ids = [c.id for c in classes_db]
    classes = [{"id": c.id, "name": c.name} for c in classes_db]
    
    divisions_db = db.query(Division).join(SchoolClass).filter(SchoolClass.academic_year_id == academic_year_id).all()
    divisions = [{"id": d.id, "class_id": d.class_id} for d in divisions_db]
    
    subjects_db = db.query(Subject).filter(Subject.class_id.in_(class_ids)).all()
    subjects = [{"id": s.id, "is_lab": s.is_lab, "double_period_allowed": s.double_period_allowed} for s in subjects_db]
    
    # We assume we have a TeacherSubject mapping mapping teachers to divisions and subjects for the workload
    # In a full app, this mapping is critical. We simulate fetching it here:
    ts_db = db.query(TeacherSubject).join(Subject).filter(Subject.class_id.in_(class_ids)).all()
    teacher_subjects = []
    
    # Use the explicit teacher-subject-division mappings configured by the admin
    for ts in ts_db:
        teacher_subjects.append({
            "teacher_id": ts.teacher_id,
            "subject_id": ts.subject_id,
            "division_id": ts.division_id,
            "weekly_periods": ts.subject.weekly_periods
        })
    
    generator = TimetableGenerator(
        teachers=teachers,
        classes=classes,
        divisions=divisions,
        subjects=subjects,
        teacher_subjects=teacher_subjects,
        days=school_setting.working_days,
        periods_per_day=school_setting.number_of_periods,
        lunch_break_period=school_setting.lunch_break_period,
        weekly_schedule=school_setting.weekly_schedule,
        global_max_weekly_teacher_periods=school_setting.max_weekly_teacher_periods
    )
    
    result = generator.generate()
    if result["status"] == "SUCCESS":
        if current_user.school.plan_type != "DEMO" and current_user.email != "sc922467@gmail.com":
            current_user.school.available_generations -= 1
            
        # Clear old slots for this academic year
        teacher_ids = [t.id for t in db.query(Teacher.id).filter(Teacher.school_id == current_user.school_id).all()]
        db.query(TimetableSlot).filter(
            TimetableSlot.teacher_id.in_(teacher_ids),
            TimetableSlot.division_id.in_([d["id"] for d in divisions])
        ).delete(synchronize_session=False)
        db.commit()
        
        # Save new slots
        for slot in result["timetable"]:
            new_slot = TimetableSlot(
                division_id=slot["division_id"],
                subject_id=slot["subject_id"],
                teacher_id=slot["teacher_id"],
                day_of_week=slot["day"],
                period_number=slot["period"],
                is_double_period=False
            )
            db.add(new_slot)
        db.commit()
        return {"message": "Timetable generated successfully"}
    else:
        raise HTTPException(status_code=400, detail=result["reason"])

@router.get("/")
def get_timetable(
    academic_year_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    academic_year_id = resolve_academic_year(db, current_user, academic_year_id)
    slots = db.query(TimetableSlot).join(Teacher).join(Division).join(SchoolClass).filter(Teacher.school_id == current_user.school_id, 
        SchoolClass.academic_year_id == academic_year_id
    ).all()
    
    return [
        {
            "id": slot.id,
            "division_id": slot.division_id,
            "division_name": slot.division.name,
            "class_name": slot.division.school_class.name,
            "subject_id": slot.subject_id,
            "subject_name": slot.subject.name,
            "teacher_id": slot.teacher_id,
            "teacher_name": slot.teacher.user.full_name if slot.teacher.user else slot.teacher.employee_id,
            "day": slot.day_of_week,
            "period": slot.period_number
        }
        for slot in slots
    ]
