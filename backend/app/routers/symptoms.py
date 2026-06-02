from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.symptom import SymptomLog
from app.schemas.symptom import SymptomLogCreate, SymptomLogOut
from app.routers.auth import get_current_user

router = APIRouter(prefix="/symptoms", tags=["Symptom Tracker"])

@router.post("", response_model=SymptomLogOut)
def log_symptoms(
    symptom_in: SymptomLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log daily symptoms. If an entry already exists for the given date, this endpoint will update the existing entry.
    """
    # Check if entry already exists for user on this date
    existing_log = db.query(SymptomLog).filter(
        SymptomLog.user_id == current_user.id,
        SymptomLog.date == symptom_in.date
    ).first()
    
    if existing_log:
        # Update existing record
        for field, value in symptom_in.dict(exclude_unset=True).items():
            setattr(existing_log, field, value)
        db.commit()
        db.refresh(existing_log)
        return existing_log
    else:
        # Create new record
        new_log = SymptomLog(
            user_id=current_user.id,
            **symptom_in.dict()
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log

@router.get("", response_model=List[SymptomLogOut])
def get_symptom_history(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve user symptom tracking logs within an optional date range, sorted by date descending.
    """
    query = db.query(SymptomLog).filter(SymptomLog.user_id == current_user.id)
    
    if start_date:
        query = query.filter(SymptomLog.date >= start_date)
    if end_date:
        query = query.filter(SymptomLog.date <= end_date)
        
    return query.order_by(SymptomLog.date.desc()).all()

@router.get("/{log_date}", response_model=SymptomLogOut)
def get_symptom_for_date(
    log_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch the symptom log details for a specific date.
    """
    log = db.query(SymptomLog).filter(
        SymptomLog.user_id == current_user.id,
        SymptomLog.date == log_date
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No symptom log entry found for {log_date}"
        )
    return log

@router.delete("/{log_date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_symptom_for_date(
    log_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the symptom log entry for a specific date.
    """
    log = db.query(SymptomLog).filter(
        SymptomLog.user_id == current_user.id,
        SymptomLog.date == log_date
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No symptom log entry found for {log_date}"
        )
        
    db.delete(log)
    db.commit()
    return None
