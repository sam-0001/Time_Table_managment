from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, RoleEnum, Teacher, Subject, SchoolClass, Division
from app.api.deps import get_current_user, require_roles
import pandas as pd
import io

router = APIRouter()

@router.post("/import/teachers")
async def import_teachers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN]))
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Expected columns: employee_id, user_id, mobile, qualification, max_weekly_periods, max_daily_periods
        required_cols = {'employee_id', 'user_id'}
        if not required_cols.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"Missing required columns. Found: {list(df.columns)}")
        
        added = 0
        for _, row in df.iterrows():
            teacher = db.query(Teacher).filter(Teacher.employee_id == str(row['employee_id'])).first()
            if not teacher:
                new_teacher = Teacher(
                    user_id=str(row['user_id']),
                    employee_id=str(row['employee_id']),
                    mobile=str(row.get('mobile', '')),
                    qualification=str(row.get('qualification', '')),
                    max_weekly_periods=int(row.get('max_weekly_periods', 32)),
                    max_daily_periods=int(row.get('max_daily_periods', 7))
                )
                db.add(new_teacher)
                added += 1
        
        db.commit()
        return {"message": f"Successfully imported {added} teachers."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/teachers")
def export_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.SUPER_ADMIN, RoleEnum.SCHOOL_ADMIN, RoleEnum.PRINCIPAL]))
):
    teachers = db.query(Teacher).all()
    
    data = []
    for t in teachers:
        data.append({
            "employee_id": t.employee_id,
            "user_id": t.user_id,
            "mobile": t.mobile,
            "qualification": t.qualification,
            "max_weekly_periods": t.max_weekly_periods,
            "max_daily_periods": t.max_daily_periods,
            "is_active": t.is_active
        })
        
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Teachers', index=False)
        
    headers = {
        'Content-Disposition': 'attachment; filename="teachers_export.xlsx"'
    }
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
