from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, School, SchoolSetting, AcademicYear, RoleEnum
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.security import create_refresh_token
from app.core.config import settings
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
    
    school = School(name=user_in.school_name, plan_type="FREE")
    db.add(school)
    db.commit()
    db.refresh(school)
    
    school_setting = SchoolSetting(
        school_id=school.id,
        working_days=6 if school.plan_type == "DEMO" else 5,
        number_of_periods=8 if school.plan_type == "DEMO" else 7,
        max_weekly_teacher_periods=48 if school.plan_type == "DEMO" else 32
    )
    db.add(school_setting)
    
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

import random
from datetime import timedelta
from app.db.models import OTPCode
from app.schemas.user import ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        return {"message": "If that email exists, an OTP has been sent."}
    
    otp = str(random.randint(100000, 999999))
    expires = datetime.utcnow() + timedelta(minutes=15)
    
    # In a real application, you would send an email here.
    # For now, we will print it to the server console.
    from app.core.email import send_otp_email
    send_otp_email(req.email, otp)
    
    otp_record = OTPCode(email=req.email, otp=otp, expires_at=expires)
    db.add(otp_record)
    db.commit()
    
    return {"message": "If that email exists, an OTP has been sent."}

@router.post("/verify-otp")
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    record = db.query(OTPCode).filter(
        OTPCode.email == req.email,
        OTPCode.otp == req.otp,
        OTPCode.used == False,
        OTPCode.expires_at > datetime.utcnow()
    ).first()
    
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    return {"message": "OTP verified successfully"}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    record = db.query(OTPCode).filter(
        OTPCode.email == req.email,
        OTPCode.otp == req.otp,
        OTPCode.used == False,
        OTPCode.expires_at > datetime.utcnow()
    ).first()
    
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = get_password_hash(req.new_password)
    record.used = True
    
    db.add(user)
    db.add(record)
    db.commit()
    
    return {"message": "Password reset successfully"}

from app.api.deps import get_current_user
from app.core.demo_data import generate_demo_data
from app.schemas.user import ChangePasswordRequest

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.hashed_password = get_password_hash(req.new_password)
    db.add(current_user)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/enter-demo")
def enter_demo(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if they already have a demo school
    demo_school_name = f"Demo_{current_user.id}"
    demo_school = db.query(School).filter(School.name == demo_school_name).first()
    
    if not demo_school:
        demo_school = School(name=demo_school_name, plan_type="DEMO")
        db.add(demo_school)
        db.commit()
        db.refresh(demo_school)
        
        school_setting = SchoolSetting(
            school_id=demo_school.id,
            working_days=6,
            number_of_periods=8,
            max_weekly_teacher_periods=48
        )
        db.add(school_setting)
        
        current_year = datetime.now().year
        academic_year = AcademicYear(
            school_id=demo_school.id,
            name=f"{current_year}-{current_year+1}",
            start_date=datetime(current_year, 4, 1),
            end_date=datetime(current_year+1, 3, 31),
            is_active=True
        )
        db.add(academic_year)
        db.commit()
        db.refresh(academic_year)
        
        from app.core.demo_data import generate_demo_data
        generate_demo_data(db, demo_school.id, academic_year.id)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": current_user.id, 
            "role": current_user.role.value,
            "school_id": demo_school.id,
            "is_demo_mode": True,
            "real_school_id": current_user.school_id
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_demo_mode": True}

@router.post("/exit-demo")
def exit_demo(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # They want to go back to their real school
    # The real school id is passed via token override in get_current_user
    real_school_id = getattr(current_user, "real_school_id", current_user.school_id)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": current_user.id, 
            "role": current_user.role.value
            # no school_id override needed for real school
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_demo_mode": False}
