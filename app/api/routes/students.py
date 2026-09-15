from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.db.models import Student, User, RoleEnum, Parent, Division
from app.api.deps import get_current_user, require_roles
from app.core.security import get_password_hash

router = APIRouter()

class StudentCreate(BaseModel):
    name: str
    email: str
    password: str = "student123"
    parent_id: Optional[str] = None
    division_id: str
    admission_number: str
    gender: str
    date_of_birth: Optional[datetime] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None

class StudentResponse(BaseModel):
    id: str
    name: str
    email: str
    admission_number: str
    division_name: Optional[str] = None
    parent_name: Optional[str] = None
    gender: Optional[str] = None

@router.get("/", response_model=List[StudentResponse])
def get_students(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    students = db.query(Student).options(joinedload(Student.user), joinedload(Student.division), joinedload(Student.parent).joinedload(Parent.user)).filter(Student.school_id == current_user.school_id).all()
    res = []
    for s in students:
        res.append({
            "id": s.id,
            "name": s.user.full_name if s.user else "Unknown",
            "email": s.user.email if s.user else "Unknown",
            "admission_number": s.admission_number or "",
            "division_name": s.division.name if s.division else "",
            "parent_name": s.parent.user.full_name if s.parent and s.parent.user else "",
            "gender": s.gender
        })
    return res

@router.post("/", response_model=StudentResponse)
def create_student(data: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    div = db.query(Division).filter(Division.id == data.division_id, Division.school_class.has(school_id=current_user.school_id)).first()
    if not div:
        raise HTTPException(status_code=404, detail="Division not found")
        
    new_user = User(
        email=data.email,
        full_name=data.name,
        hashed_password=get_password_hash(data.password),
        role=RoleEnum.STUDENT,
        school_id=current_user.school_id
    )
    db.add(new_user)
    db.flush()
    
    new_student = Student(
        user_id=new_user.id,
        school_id=current_user.school_id,
        parent_id=data.parent_id,
        division_id=data.division_id,
        admission_number=data.admission_number,
        gender=data.gender,
        date_of_birth=data.date_of_birth,
        blood_group=data.blood_group,
        address=data.address
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return {
        "id": new_student.id,
        "name": new_user.full_name,
        "email": new_user.email,
        "admission_number": new_student.admission_number,
        "division_name": div.name,
        "parent_name": "", # just return empty for newly created object for simplicity
        "gender": new_student.gender
    }

@router.delete("/{id}")
def delete_student(id: str, db: Session = Depends(get_db), current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))):
    student = db.query(Student).filter(Student.id == id, Student.school_id == current_user.school_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student.user)
    db.commit()
    return {"message": "Student deleted"}
