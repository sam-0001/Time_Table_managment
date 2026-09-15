from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.db.models import Announcement, User, RoleEnum
from app.api.deps import get_current_user

router = APIRouter()

class AnnouncementCreate(BaseModel):
    title: str
    description: str
    division_id: Optional[str] = None

class AnnouncementResponse(BaseModel):
    id: str
    title: str
    description: str
    date: datetime
    division_id: Optional[str]
    division_name: Optional[str]

@router.get("/", response_model=List[AnnouncementResponse])
def get_announcements(division_id: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Announcement).filter(Announcement.school_id == current_user.school_id)
    if division_id:
        # Get division specific AND school-wide announcements
        query = query.filter((Announcement.division_id == division_id) | (Announcement.division_id == None))
    
    announcements = query.order_by(Announcement.date.desc()).all()
    
    res = []
    for a in announcements:
        res.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "date": a.date,
            "division_id": a.division_id,
            "division_name": a.division.name if a.division else "School Wide"
        })
    return res

@router.post("/", response_model=AnnouncementResponse)
def create_announcement(data: AnnouncementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Optional: Check if user has permission to post (e.g., admin or principal)
    new_a = Announcement(
        school_id=current_user.school_id,
        division_id=data.division_id if data.division_id else None,
        title=data.title,
        description=data.description,
        date=datetime.utcnow()
    )
    db.add(new_a)
    db.commit()
    db.refresh(new_a)
    
    return {
        "id": new_a.id,
        "title": new_a.title,
        "description": new_a.description,
        "date": new_a.date,
        "division_id": new_a.division_id,
        "division_name": new_a.division.name if new_a.division else "School Wide"
    }

@router.delete("/{id}")
def delete_announcement(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ann = db.query(Announcement).filter(Announcement.id == id, Announcement.school_id == current_user.school_id).first()
    if not ann:
        raise HTTPException(status_code=404)
    db.delete(ann)
    db.commit()
    return {"message": "Deleted"}
