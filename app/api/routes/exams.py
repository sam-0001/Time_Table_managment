from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from app.db.database import get_db
from app.db.models import Exam, ExamResult, Student, User, RoleEnum
from app.api.deps import get_current_user

router = APIRouter()

class ExamCreate(BaseModel):
    name: str
    date: date
    division_id: str
    subject_id: str
    max_marks: float = 100.0

class ExamResponse(BaseModel):
    id: str
    name: str
    date: date
    division_id: str
    subject_id: str
    max_marks: float
    division_name: str
    subject_name: str

class ResultRecord(BaseModel):
    student_id: str
    score: Optional[float] = None
    remarks: Optional[str] = None

class ExamResultsSave(BaseModel):
    records: List[ResultRecord]

class ExamResultResponse(BaseModel):
    student_id: str
    student_name: str
    admission_number: str
    score: Optional[float] = None
    remarks: Optional[str] = None

@router.get("/", response_model=List[ExamResponse])
def get_exams(division_id: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Exam).filter(Exam.school_id == current_user.school_id)
    if division_id:
        query = query.filter(Exam.division_id == division_id)
    exams = query.order_by(Exam.date.desc()).all()
    
    res = []
    for e in exams:
        res.append({
            "id": e.id,
            "name": e.name,
            "date": e.date.date(),
            "division_id": e.division_id,
            "subject_id": e.subject_id,
            "max_marks": e.max_marks,
            "division_name": e.division.name if e.division else "",
            "subject_name": e.subject.name if e.subject else ""
        })
    return res

@router.post("/", response_model=ExamResponse)
def create_exam(data: ExamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dt = datetime.combine(data.date, datetime.min.time())
    new_exam = Exam(
        school_id=current_user.school_id,
        division_id=data.division_id,
        subject_id=data.subject_id,
        name=data.name,
        date=dt,
        max_marks=data.max_marks
    )
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    
    return {
        "id": new_exam.id,
        "name": new_exam.name,
        "date": new_exam.date.date(),
        "division_id": new_exam.division_id,
        "subject_id": new_exam.subject_id,
        "max_marks": new_exam.max_marks,
        "division_name": new_exam.division.name if new_exam.division else "",
        "subject_name": new_exam.subject.name if new_exam.subject else ""
    }

@router.delete("/{id}")
def delete_exam(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exam = db.query(Exam).filter(Exam.id == id, Exam.school_id == current_user.school_id).first()
    if not exam:
        raise HTTPException(status_code=404)
    db.delete(exam)
    db.commit()
    return {"message": "Deleted"}

@router.get("/{id}/results", response_model=List[ExamResultResponse])
def get_exam_results(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exam = db.query(Exam).filter(Exam.id == id, Exam.school_id == current_user.school_id).first()
    if not exam:
        raise HTTPException(status_code=404)
        
    students = db.query(Student).filter(Student.division_id == exam.division_id, Student.school_id == current_user.school_id).all()
    results = db.query(ExamResult).filter(ExamResult.exam_id == id).all()
    res_map = {r.student_id: r for r in results}
    
    output = []
    for s in students:
        r = res_map.get(s.id)
        output.append({
            "student_id": s.id,
            "student_name": s.user.full_name if s.user else "Unknown",
            "admission_number": s.admission_number or "",
            "score": r.score if r else None,
            "remarks": r.remarks if r else None
        })
    return output

@router.post("/{id}/results")
def save_exam_results(id: str, data: ExamResultsSave, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exam = db.query(Exam).filter(Exam.id == id, Exam.school_id == current_user.school_id).first()
    if not exam:
        raise HTTPException(status_code=404)
        
    results = db.query(ExamResult).filter(ExamResult.exam_id == id).all()
    res_map = {r.student_id: r for r in results}
    
    for record in data.records:
        if record.student_id in res_map:
            res_map[record.student_id].score = record.score
            res_map[record.student_id].remarks = record.remarks
        else:
            new_r = ExamResult(
                exam_id=id,
                student_id=record.student_id,
                score=record.score,
                remarks=record.remarks
            )
            db.add(new_r)
    db.commit()
    return {"message": "Results saved"}
