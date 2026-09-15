from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from app.db.database import get_db
from app.db.models import Attendance, Student, User, RoleEnum
from app.api.deps import get_current_user

router = APIRouter()

class AttendanceRecord(BaseModel):
    student_id: str
    status: str
    remarks: Optional[str] = None

class AttendanceBulkSave(BaseModel):
    division_id: str
    date: date
    records: List[AttendanceRecord]

class AttendanceResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    admission_number: str
    date: date
    status: str
    remarks: Optional[str] = None

@router.get("/", response_model=List[AttendanceResponse])
def get_attendance(division_id: str, date: date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Get all students in the division
    students = db.query(Student).filter(Student.division_id == division_id, Student.school_id == current_user.school_id).all()
    
    # Get attendance for that date
    # Note: date is a python date object, we might need to query safely
    attendances = db.query(Attendance).filter(
        Attendance.division_id == division_id,
        Attendance.school_id == current_user.school_id
    ).all()
    
    # Filter by date exactly (assuming stored at 00:00:00)
    attendances = [a for a in attendances if a.date.date() == date]
    
    att_map = {a.student_id: a for a in attendances}
    
    res = []
    for s in students:
        a = att_map.get(s.id)
        res.append({
            "id": a.id if a else "",
            "student_id": s.id,
            "student_name": s.user.full_name if s.user else "Unknown",
            "admission_number": s.admission_number or "",
            "date": date,
            "status": a.status if a else "PRESENT", # Default if not marked
            "remarks": a.remarks if a else ""
        })
    return res

@router.post("/")
def save_attendance(data: AttendanceBulkSave, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target_dt = datetime.combine(data.date, datetime.min.time())
    
    # Fetch existing
    existing = db.query(Attendance).filter(
        Attendance.division_id == data.division_id,
        Attendance.school_id == current_user.school_id
    ).all()
    existing = [a for a in existing if a.date.date() == data.date]
    existing_map = {a.student_id: a for a in existing}
    
    for record in data.records:
        if record.student_id in existing_map:
            att = existing_map[record.student_id]
            att.status = record.status
            att.remarks = record.remarks
            att.recorded_by_id = current_user.id
        else:
            att = Attendance(
                school_id=current_user.school_id,
                student_id=record.student_id,
                division_id=data.division_id,
                recorded_by_id=current_user.id,
                date=target_dt,
                status=record.status,
                remarks=record.remarks
            )
            db.add(att)
            
    db.commit()
    return {"message": "Attendance saved successfully"}
