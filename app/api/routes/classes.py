from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import SchoolClass, Division, User, RoleEnum, AcademicYear
from app.api.deps import get_current_user, require_roles
from pydantic import BaseModel

router = APIRouter()

class DivisionCreate(BaseModel):
    name: str
    class_teacher_id: Optional[str] = None
    classroom_id: Optional[str] = None

class ClassCreate(BaseModel):
    academic_year_id: str
    name: str
    level: int
    divisions: List[DivisionCreate] = []

class DivisionResponse(DivisionCreate):
    id: str
    class_id: str

    class Config:
        from_attributes = True

class ClassResponse(BaseModel):
    id: str
    academic_year_id: str
    name: str
    level: int
    divisions: List[DivisionResponse] = []

    class Config:
        from_attributes = True

@router.post("/", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_in: ClassCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    school_class = db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == current_user.school_id, 
        SchoolClass.name == class_in.name, 
        SchoolClass.academic_year_id == class_in.academic_year_id
    ).first()
    
    if school_class:
        raise HTTPException(status_code=400, detail="Class with this name already exists for the academic year.")
        
    new_class = SchoolClass(
        academic_year_id=class_in.academic_year_id,
        name=class_in.name,
        level=class_in.level
    )
    db.add(new_class)
    db.flush()
    
    for div_in in class_in.divisions:
        new_div = Division(
            class_id=new_class.id,
            name=div_in.name,
            class_teacher_id=div_in.class_teacher_id,
            classroom_id=div_in.classroom_id
        )
        db.add(new_div)
        
    db.commit()
    db.refresh(new_class)
    return new_class

@router.get("/", response_model=List[ClassResponse])
def get_classes(
    academic_year_id: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == current_user.school_id)
    if academic_year_id:
        query = query.filter(SchoolClass.academic_year_id == academic_year_id)
    return query.offset(skip).limit(limit).all()

@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: str,
    class_in: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    school_class = db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == current_user.school_id, SchoolClass.id == class_id).first()
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    school_class.name = class_in.name
    school_class.level = class_in.level
    
    # Update divisions: for simplicity, drop old and recreate
    db.query(Division).filter(Division.class_id == class_id).delete()
    for div_in in class_in.divisions:
        new_div = Division(
            class_id=school_class.id,
            name=div_in.name,
            class_teacher_id=div_in.class_teacher_id,
            classroom_id=div_in.classroom_id
        )
        db.add(new_div)
        
    db.commit()
    db.refresh(school_class)
    return school_class

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    school_class = db.query(SchoolClass).join(AcademicYear).filter(AcademicYear.school_id == current_user.school_id, SchoolClass.id == class_id).first()
    if not school_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    db.delete(school_class)
    db.commit()
    return None
