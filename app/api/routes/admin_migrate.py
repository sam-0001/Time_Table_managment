from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter()

@router.get("/migrate-school")
def migrate_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("ALTER TABLE schools ADD COLUMN plan_type VARCHAR DEFAULT 'DEMO'"))
        db.execute(text("ALTER TABLE schools ADD COLUMN available_generations INTEGER DEFAULT 0"))
        db.commit()
        return {"status": "Migration finished"}
    except Exception as e:
        db.rollback()
        return {"status": "Error", "message": str(e)}
