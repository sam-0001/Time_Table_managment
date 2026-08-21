from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter()

@router.get("/migrate-is-demo")
def migrate_db(db: Session = Depends(get_db)):
    tables = ['users', 'teachers', 'classes', 'divisions', 'subjects']
    results = {}
    for table in tables:
        try:
            db.execute(text(f"ALTER TABLE {table} ADD COLUMN is_demo BOOLEAN DEFAULT FALSE"))
            db.commit()
            results[table] = "Success"
        except Exception as e:
            db.rollback()
            results[table] = str(e)
            
    return {"status": "Migration finished", "results": results}
