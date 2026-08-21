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
