from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, School, SchoolSetting, AcademicYear, RoleEnum
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.schemas.user import Token, User as UserSchema, UserCreate, SchoolRegisterCreate
from datetime import datetime

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role.value})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=UserSchema)
def register_school(user_in: SchoolRegisterCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    school = School(name=user_in.school_name)
    db.add(school)
    db.commit()
    db.refresh(school)
    
    settings = SchoolSetting(school_id=school.id)
    db.add(settings)
    
    current_year = datetime.now().year
    academic_year = AcademicYear(
        school_id=school.id,
        name=f"{current_year}-{current_year+1}",
        start_date=datetime(current_year, 4, 1),
        end_date=datetime(current_year+1, 3, 31),
        is_active=True
    )
    db.add(academic_year)
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=RoleEnum.SCHOOL_ADMIN,
        school_id=school.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
