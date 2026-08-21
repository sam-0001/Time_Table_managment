from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.db.database import get_db
from app.db.models import TeacherLeave, Teacher, TimetableSlot, Substitution, User, RoleEnum
from app.api.deps import get_current_user, require_roles
from pydantic import BaseModel
import random

router = APIRouter()

class LeaveCreate(BaseModel):
    teacher_id: str
    date: date
    leave_type: str = "FULL"
    reason: Optional[str] = None

class LeaveResponse(LeaveCreate):
    id: str

    class Config:
        from_attributes = True

@router.post("/", response_model=LeaveResponse, status_code=status.HTTP_201_CREATED)
def mark_leave(
    leave_in: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL, RoleEnum.TIMETABLE_COORDINATOR]))
):
    leave_datetime = datetime.combine(leave_in.date, datetime.min.time())
    
    # Check if leave already exists
    existing = db.query(TeacherLeave).filter(
        TeacherLeave.teacher_id == leave_in.teacher_id,
        TeacherLeave.date == leave_datetime
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Leave already marked for this teacher on this date.")
        
    leave = TeacherLeave(
        teacher_id=leave_in.teacher_id,
        date=leave_datetime,
        leave_type=leave_in.leave_type,
        reason=leave_in.reason
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave

@router.post("/generate-arrangements", status_code=status.HTTP_200_OK)
def generate_arrangements(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL, RoleEnum.TIMETABLE_COORDINATOR]))
):
    leave_datetime = datetime.combine(target_date, datetime.min.time())
    day_of_week = target_date.weekday() # 0 = Monday
    
    # 1. Get all leaves for the date
    leaves = db.query(TeacherLeave).join(Teacher).filter(Teacher.school_id == current_user.school_id, TeacherLeave.date == leave_datetime).all()
    absent_teacher_dict = {l.teacher_id: l.leave_type for l in leaves}
    
    if not absent_teacher_dict:
        return {"message": "No teachers are on leave.", "substitutions_made": 0}
        
    absent_teacher_ids = list(absent_teacher_dict.keys())
        
    # 2. Get affected timetable slots
    all_affected_slots = db.query(TimetableSlot).filter(
        TimetableSlot.teacher_id.in_(absent_teacher_ids),
        TimetableSlot.day_of_week == day_of_week
    ).all()
    
    # Get total periods today for rule validation
    from app.db.models import SchoolSetting
    setting = db.query(SchoolSetting).filter(SchoolSetting.school_id == current_user.school_id).first()
    periods_today = setting.number_of_periods if setting else 7
    lunch_period = setting.lunch_break_period if setting else 4
    if setting and setting.weekly_schedule:
        day_conf = next((d for d in setting.weekly_schedule if d["day"] == day_of_week and d.get("is_working")), None)
        if day_conf:
            periods_today = day_conf["periods"]
            if day_conf.get("lunch_period") is not None:
                lunch_period = day_conf["lunch_period"]
                
    affected_slots = []
    for slot in all_affected_slots:
        l_type = absent_teacher_dict[slot.teacher_id]
        if l_type == "FULL":
            affected_slots.append(slot)
        elif l_type == "FIRST_HALF" and slot.period_number < lunch_period:
            affected_slots.append(slot)
        elif l_type == "SECOND_HALF" and slot.period_number > lunch_period: # After lunch break
            affected_slots.append(slot)
            
    # Track busy teachers per period and daily loads
    active_teachers = db.query(Teacher).filter(Teacher.school_id == current_user.school_id, Teacher.is_active == True).all()
    today_slots = db.query(TimetableSlot).join(Teacher).filter(Teacher.school_id == current_user.school_id, TimetableSlot.day_of_week == day_of_week).all()
    today_subs = db.query(Substitution).join(TimetableSlot).join(Teacher).filter(Teacher.school_id == current_user.school_id, Substitution.date == leave_datetime).all()
    
    daily_loads = {t.id: 0 for t in active_teachers}
    busy_teachers_per_period = {p: set() for p in range(periods_today)}
    
    for tid, l_type in absent_teacher_dict.items():
        for p in range(periods_today):
            if l_type == "FULL":
                busy_teachers_per_period[p].add(tid)
            elif l_type == "FIRST_HALF" and p < lunch_period:
                busy_teachers_per_period[p].add(tid)
            elif l_type == "SECOND_HALF" and p > lunch_period:
                busy_teachers_per_period[p].add(tid)
    
    for s in today_slots:
        if s.teacher_id in daily_loads:
            daily_loads[s.teacher_id] += 1
        if s.period_number not in busy_teachers_per_period:
            busy_teachers_per_period[s.period_number] = set()
        busy_teachers_per_period[s.period_number].add(s.teacher_id)
        
    for sub in today_subs:
        if sub.substitute_teacher_id in daily_loads:
            daily_loads[sub.substitute_teacher_id] += 1
        period = sub.original_slot.period_number
        if period not in busy_teachers_per_period:
            busy_teachers_per_period[period] = set()
        busy_teachers_per_period[period].add(sub.substitute_teacher_id)
    
    subs_made = 0
    for slot in affected_slots:
        period = slot.period_number
        busy_ids = busy_teachers_per_period.get(period, set())
        
        candidates = []
        for t in active_teachers:
            if t.id in busy_ids:
                continue
            
            # Enforce daily limit: always one less than total periods today
            max_allowed = max(0, periods_today - 1)
            if daily_loads[t.id] >= max_allowed:
                continue
                
            candidates.append(t)
            
        if candidates:
            # Sort by lowest daily load
            candidates.sort(key=lambda x: daily_loads[x.id])
            
            # Find best group for fair distribution
            best_load = daily_loads[candidates[0].id]
            best_candidates = [c for c in candidates if daily_loads[c.id] == best_load]
            
            sub_teacher = random.choice(best_candidates)
            
            sub = Substitution(
                date=leave_datetime,
                original_slot_id=slot.id,
                substitute_teacher_id=sub_teacher.id
            )
            db.add(sub)
            subs_made += 1
            
            # Update tracking
            daily_loads[sub_teacher.id] += 1
            busy_teachers_per_period[period].add(sub_teacher.id)
            
    db.commit()
    return {"message": "Arrangements generated.", "substitutions_made": subs_made}

@router.get("/")
def get_leaves(
    date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave_datetime = datetime.combine(date, datetime.min.time())
    leaves = db.query(TeacherLeave).join(Teacher).filter(Teacher.school_id == current_user.school_id, TeacherLeave.date == leave_datetime).all()
    
    return [
        {
            "id": l.id,
            "teacher_id": l.teacher_id,
            "teacher_name": l.teacher.user.full_name if l.teacher.user else l.teacher.employee_id,
            "date": l.date.date(),
            "leave_type": l.leave_type,
            "reason": l.reason
        }
        for l in leaves
    ]

@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(
    leave_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL, RoleEnum.TIMETABLE_COORDINATOR]))
):
    leave = db.query(TeacherLeave).join(Teacher).filter(TeacherLeave.id == leave_id, Teacher.school_id == current_user.school_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
        
    db.delete(leave)
    db.commit()
    return None

@router.get("/arrangements")
def get_arrangements(
    date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    leave_datetime = datetime.combine(date, datetime.min.time())
    subs = db.query(Substitution).join(TimetableSlot).join(Teacher).filter(Teacher.school_id == current_user.school_id, Substitution.date == leave_datetime).all()
    
    return [
        {
            "id": sub.id,
            "substitute_teacher_name": sub.substitute_teacher.user.full_name if sub.substitute_teacher.user else sub.substitute_teacher.employee_id,
            "original_teacher_name": sub.original_slot.teacher.user.full_name if sub.original_slot.teacher.user else sub.original_slot.teacher.employee_id,
            "division_name": f"{sub.original_slot.division.school_class.name}-{sub.original_slot.division.name}",
            "subject_name": sub.original_slot.subject.name,
            "period": sub.original_slot.period_number
        }
        for sub in subs
    ]
