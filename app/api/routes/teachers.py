from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Teacher, User, RoleEnum
from app.api.deps import get_current_user, require_roles
from pydantic import BaseModel

router = APIRouter()

class TeacherAssignmentSchema(BaseModel):
    subject_id: str
    division_id: str

class TeacherCreate(BaseModel):
    name: str
    email: str | None = None
    employee_id: str | None = None
    mobile: str | None = None
    qualification: str | None = None
    assignments: List[TeacherAssignmentSchema] = []
    max_daily_periods: int = 7
    max_weekly_periods: int = 32
    class_teacher_of_division_id: str | None = None

class TeacherUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    employee_id: str | None = None
    mobile: str | None = None
    qualification: str | None = None
    assignments: List[TeacherAssignmentSchema] | None = None
    max_daily_periods: int | None = None
    max_weekly_periods: int | None = None
    is_active: bool | None = None
    class_teacher_of_division_id: str | None = None

class TeacherResponse(BaseModel):
    id: str
    employee_id: str
    mobile: str | None
    qualification: str | None
    max_daily_periods: int
    max_weekly_periods: int
    is_active: bool
    
    # We will compute name and email from the related User
    name: str | None = None
    email: str | None = None
    assignments: List[TeacherAssignmentSchema] = []
    class_teacher_of_division_id: str | None = None

    class Config:
        from_attributes = True

@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    teacher_in: TeacherCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    if not teacher_in.employee_id:
        max_id = 0
        for t in db.query(Teacher.employee_id).all():
            if t[0] and t[0].isdigit():
                max_id = max(max_id, int(t[0]))
        teacher_in.employee_id = str(max_id + 1)
        
    teacher = db.query(Teacher).filter(Teacher.employee_id == teacher_in.employee_id).first()
    if teacher:
        raise HTTPException(status_code=400, detail="Teacher with this Employee ID already exists.")
        
    email_to_use = teacher_in.email if teacher_in.email else f"{teacher_in.employee_id.lower()}@school.edu"
    
    user = db.query(User).filter(User.email == email_to_use).first()
    if user:
        existing_teacher_for_user = db.query(Teacher).filter(Teacher.user_id == user.id).first()
        if existing_teacher_for_user:
            raise HTTPException(status_code=400, detail="A teacher with this email already exists.")
    else:
        from app.core.security import get_password_hash
        user = User(
            email=email_to_use,
            full_name=teacher_in.name,
            hashed_password=get_password_hash("password123"),
            role=RoleEnum.TEACHER
        )
        db.add(user)
        db.flush()
        
    new_teacher = Teacher(
        user_id=user.id,
        employee_id=teacher_in.employee_id,
        mobile=teacher_in.mobile,
        qualification=teacher_in.qualification,
        max_daily_periods=teacher_in.max_daily_periods,
        max_weekly_periods=teacher_in.max_weekly_periods
    )
    db.add(new_teacher)
    db.flush()
    
    from app.db.models import TeacherSubject, Division
    for assign in teacher_in.assignments:
        ts = TeacherSubject(teacher_id=new_teacher.id, subject_id=assign.subject_id, division_id=assign.division_id)
        db.add(ts)
        
    if teacher_in.class_teacher_of_division_id:
        div = db.query(Division).filter(Division.id == teacher_in.class_teacher_of_division_id).first()
        if div:
            div.class_teacher_id = new_teacher.id
            db.add(div)
        
    db.commit()
    db.refresh(new_teacher)
    
    return {
        "id": new_teacher.id,
        "employee_id": new_teacher.employee_id,
        "mobile": new_teacher.mobile,
        "qualification": new_teacher.qualification,
        "max_daily_periods": new_teacher.max_daily_periods,
        "max_weekly_periods": new_teacher.max_weekly_periods,
        "is_active": new_teacher.is_active,
        "name": user.full_name,
        "email": user.email,
        "assignments": [TeacherAssignmentSchema(subject_id=a.subject_id, division_id=a.division_id) for a in teacher_in.assignments],
        "class_teacher_of_division_id": new_teacher.class_teacher_of.id if new_teacher.class_teacher_of else None
    }

@router.get("/", response_model=List[TeacherResponse])
def get_teachers(
    skip: int = 0, 
    limit: int = 100, 
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Teacher)
    if search:
        query = query.filter(Teacher.employee_id.ilike(f"%{search}%"))
    teachers = query.offset(skip).limit(limit).all()
    
    result = []
    for t in teachers:
        user = t.user
        assigns = [{"subject_id": ts.subject_id, "division_id": ts.division_id} for ts in t.subjects]
        result.append({
            "id": t.id,
            "employee_id": t.employee_id,
            "mobile": t.mobile,
            "qualification": t.qualification,
            "max_daily_periods": t.max_daily_periods,
            "max_weekly_periods": t.max_weekly_periods,
            "is_active": t.is_active,
            "name": user.full_name if user else None,
            "email": user.email if user else None,
            "assignments": assigns,
            "class_teacher_of_division_id": t.class_teacher_of.id if t.class_teacher_of else None
        })
    return result

@router.get("/{id}", response_model=TeacherResponse)
def get_teacher(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = db.query(Teacher).filter(Teacher.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
    user = t.user
    assigns = [{"subject_id": ts.subject_id, "division_id": ts.division_id} for ts in t.subjects]
    return {
        "id": t.id,
        "employee_id": t.employee_id,
        "mobile": t.mobile,
        "qualification": t.qualification,
        "max_daily_periods": t.max_daily_periods,
        "max_weekly_periods": t.max_weekly_periods,
        "is_active": t.is_active,
        "name": user.full_name if user else None,
        "email": user.email if user else None,
        "assignments": assigns,
        "class_teacher_of_division_id": t.class_teacher_of.id if t.class_teacher_of else None
    }

@router.put("/{id}", response_model=TeacherResponse)
def update_teacher(
    id: str,
    teacher_in: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    t = db.query(Teacher).filter(Teacher.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
        
    update_data = teacher_in.model_dump(exclude_unset=True)
    if "assignments" in update_data:
        # Delete old
        from app.db.models import TeacherSubject, Division
        db.query(TeacherSubject).filter(TeacherSubject.teacher_id == id).delete()
        # Add new
        for assign in update_data["assignments"]:
            ts = TeacherSubject(teacher_id=id, subject_id=assign["subject_id"], division_id=assign["division_id"])
            db.add(ts)
        del update_data["assignments"]

    if "class_teacher_of_division_id" in update_data:
        from app.db.models import Division
        # Clear existing
        existing_divs = db.query(Division).filter(Division.class_teacher_id == id).all()
        for d in existing_divs:
            d.class_teacher_id = None
            db.add(d)
        
        new_div_id = update_data.pop("class_teacher_of_division_id")
        if new_div_id:
            new_div = db.query(Division).filter(Division.id == new_div_id).first()
            if new_div:
                new_div.class_teacher_id = id
                db.add(new_div)

    for field, value in update_data.items():
        if field in ["name", "email"]:
            continue # handled below
        setattr(t, field, value)
        
    user = t.user
    if user:
        if teacher_in.name is not None:
            user.full_name = teacher_in.name
        if teacher_in.email is not None:
            new_email = teacher_in.email if teacher_in.email else f"{t.employee_id.lower()}@school.edu"
            if new_email != user.email:
                existing_user = db.query(User).filter(User.email == new_email).first()
                if existing_user:
                    raise HTTPException(status_code=400, detail="Email is already in use by another user.")
            user.email = new_email
        db.add(user)
        
    db.commit()
    db.refresh(t)
    
    user = t.user
    assigns = [{"subject_id": ts.subject_id, "division_id": ts.division_id} for ts in t.subjects]
    return {
        "id": t.id,
        "employee_id": t.employee_id,
        "mobile": t.mobile,
        "qualification": t.qualification,
        "max_daily_periods": t.max_daily_periods,
        "max_weekly_periods": t.max_weekly_periods,
        "is_active": t.is_active,
        "name": user.full_name if user else None,
        "email": user.email if user else None,
        "assignments": assigns,
        "class_teacher_of_division_id": t.class_teacher_of.id if t.class_teacher_of else None
    }

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    teacher = db.query(Teacher).filter(Teacher.id == id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    db.delete(teacher)
    db.commit()
    return None
