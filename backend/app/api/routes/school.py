from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import School, SchoolSetting, AcademicYear, User
from app.api.deps import get_current_user
from pydantic import BaseModel
from datetime import time, datetime

router = APIRouter()

class SchoolSettingsCreate(BaseModel):
    working_days: int = 5
    start_time: time
    end_time: time
    number_of_periods: int = 7
    period_duration: int
    lunch_break_period: int = 4
    assembly_duration: int
    weekly_schedule: list = None
    total_weekly_periods: int = 40
    max_weekly_teacher_periods: int = 32

class SchoolSettingsUpdate(BaseModel):
    working_days: int = None
    start_time: time = None
    end_time: time = None
    number_of_periods: int = None
    period_duration: int = None
    lunch_break_period: int = None
    assembly_duration: int = None
    weekly_schedule: list = None
    total_weekly_periods: int = None
    max_weekly_teacher_periods: int = None

class SchoolCreate(BaseModel):
    name: str
    code: str
    address: str = ""
    city: str = ""
    state: str = ""
    pincode: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    board: str = ""
    medium: str = ""
    settings: SchoolSettingsCreate

class AcademicYearCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    is_active: bool = False

@router.post("/setup", status_code=status.HTTP_201_CREATED)
def setup_school(school_in: SchoolCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(School).first()
    if existing:
        raise HTTPException(status_code=400, detail="School is already set up.")
        
    new_school = School(
        name=school_in.name,
        code=school_in.code,
        address=school_in.address,
        city=school_in.city,
        state=school_in.state,
        pincode=school_in.pincode,
        phone=school_in.phone,
        email=school_in.email,
        website=school_in.website,
        board=school_in.board,
        medium=school_in.medium
    )
    db.add(new_school)
    db.flush()
    
    settings = SchoolSetting(
        school_id=new_school.id,
        working_days=school_in.settings.working_days,
        start_time=school_in.settings.start_time,
        end_time=school_in.settings.end_time,
        number_of_periods=school_in.settings.number_of_periods,
        period_duration=school_in.settings.period_duration,
        lunch_break_period=school_in.settings.lunch_break_period,
        assembly_duration=school_in.settings.assembly_duration,
        weekly_schedule=school_in.settings.weekly_schedule,
        total_weekly_periods=school_in.settings.total_weekly_periods
    )
    db.add(settings)
    db.commit()
    db.refresh(new_school)
    return {"message": "School setup successfully", "school_id": new_school.id}

@router.post("/academic-year", status_code=status.HTTP_201_CREATED)
def create_academic_year(year_in: AcademicYearCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    school = db.query(School).first()
    if not school:
        raise HTTPException(status_code=400, detail="School not set up.")
        
    year = AcademicYear(
        school_id=school.id,
        name=year_in.name,
        start_date=year_in.start_date,
        end_date=year_in.end_date,
        is_active=year_in.is_active
    )
    db.add(year)
    db.commit()
    return {"message": "Academic year created", "id": year.id}

@router.get("/settings")
def get_school_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    settings = db.query(SchoolSetting).first()
    if not settings:
        # Fallback: Create default school and settings if missing
        school = db.query(School).first()
        if not school:
            school = School(name="My School", code="SCH", address="", city="", state="", pincode="", phone="", email="", website="", board="", medium="")
            db.add(school)
            db.flush()
        
        settings = SchoolSetting(
            school_id=school.id,
            working_days=5,
            start_time=time(8, 0),
            end_time=time(14, 0),
            number_of_periods=7,
            period_duration=45,
            lunch_break_period=4,
            assembly_duration=15,
            total_weekly_periods=35
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings

@router.put("/settings")
def update_school_settings(settings_in: SchoolSettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    settings = db.query(SchoolSetting).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
        
    db.commit()
    db.refresh(settings)
    return settings
