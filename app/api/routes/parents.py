from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import Parent, User, RoleEnum
from app.api.deps import get_current_user, require_roles
from app.core.security import get_password_hash

router = APIRouter()

class ParentCreate(BaseModel):
    name: str
    email: str
    phone: str
    address: Optional[str] = None
    blood_group: Optional[str] = None
    password: str = "parent123"

class ParentResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None

@router.get("/", response_model=List[ParentResponse])
def get_parents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    parents = db.query(Parent).filter(Parent.school_id == current_user.school_id).all()
    res = []
    for p in parents:
        res.append({
            "id": p.id,
            "name": p.user.full_name,
            "email": p.user.email,
            "phone": p.phone,
            "address": p.address,
            "blood_group": p.blood_group
        })
    return res

@router.post("/", response_model=ParentResponse)
def create_parent(data: ParentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))):
    # Check if user email exists
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = User(
        email=data.email,
        full_name=data.name,
        hashed_password=get_password_hash(data.password),
        role=RoleEnum.PARENT,
        school_id=current_user.school_id
    )
    db.add(new_user)
    db.flush()
    
    new_parent = Parent(
        user_id=new_user.id,
        school_id=current_user.school_id,
        phone=data.phone,
        address=data.address,
        blood_group=data.blood_group
    )
    db.add(new_parent)
    db.commit()
    db.refresh(new_parent)
    
    return {
        "id": new_parent.id,
        "name": new_user.full_name,
        "email": new_user.email,
        "phone": new_parent.phone,
        "address": new_parent.address,
        "blood_group": new_parent.blood_group
    }

@router.delete("/{id}")
def delete_parent(id: str, db: Session = Depends(get_db), current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))):
    parent = db.query(Parent).filter(Parent.id == id, Parent.school_id == current_user.school_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
        
    db.delete(parent.user) # cascades to parent
    db.commit()
    return {"message": "Parent deleted"}
