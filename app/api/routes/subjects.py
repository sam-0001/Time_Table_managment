from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Subject, User, RoleEnum
from app.api.deps import get_current_user, require_roles
from pydantic import BaseModel

router = APIRouter()

class SubjectCreate(BaseModel):
    class_id: str
    name: str
    code: str
    weekly_periods: int = 5
    double_period_allowed: bool = False
    is_lab: bool = False

class SubjectUpdate(BaseModel):
    name: str = None
    code: str = None
    weekly_periods: int = None
    double_period_allowed: bool = None
    is_lab: bool = None

class SubjectResponse(SubjectCreate):
    id: str

    class Config:
        from_attributes = True

@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_in: SubjectCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL, RoleEnum.TIMETABLE_COORDINATOR]))
):
    subject = db.query(Subject).filter(Subject.code == subject_in.code, Subject.class_id == subject_in.class_id).first()
    if subject:
        raise HTTPException(status_code=400, detail="Subject with this code already exists for the class.")
        
    new_subject = Subject(
        class_id=subject_in.class_id,
        name=subject_in.name,
        code=subject_in.code,
        weekly_periods=subject_in.weekly_periods,
        double_period_allowed=subject_in.double_period_allowed,
        is_lab=subject_in.is_lab
    )
    try:
        db.add(new_subject)
        db.commit()
        db.refresh(new_subject)
        return new_subject
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Subject with this code already exists for the class.")

@router.get("/", response_model=List[SubjectResponse])
def get_subjects(
    class_id: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    search: str = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    query = db.query(Subject)
    if class_id:
        query = query.filter(Subject.class_id == class_id)
    if search:
        query = query.filter(Subject.name.ilike(f"%{search}%") | Subject.code.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@router.put("/{id}", response_model=SubjectResponse)
def update_subject(
    id: str,
    subject_in: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    subject = db.query(Subject).filter(Subject.id == id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    if subject_in.code:
        existing_subject = db.query(Subject).filter(Subject.code == subject_in.code, Subject.class_id == subject.class_id, Subject.id != id).first()
        if existing_subject:
            raise HTTPException(status_code=400, detail="Subject with this code already exists for the class.")

    update_data = subject_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)
        
    try:
        db.commit()
        db.refresh(subject)
        return subject
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Subject with this code already exists for the class.")

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    subject = db.query(Subject).filter(Subject.id == id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(subject)
    db.commit()
    return None
