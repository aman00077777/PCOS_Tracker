from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.cycle import CycleLog
from app.schemas.cycle import CycleLogCreate, CycleLogUpdate, CycleLogOut, CyclePrediction
from app.routers.auth import get_current_user
from app.services.recommendations import get_cycle_phase, get_phase_recommendations

router = APIRouter(prefix="/cycles", tags=["Cycle Tracker"])

@router.post("", response_model=CycleLogOut)
def start_new_cycle(
    cycle_in: CycleLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a new menstrual cycle (period start date). Calculates cycle length based on previous cycle.
    """
    # Check if a cycle log already exists for this exact start date
    existing_log = db.query(CycleLog).filter(
        CycleLog.user_id == current_user.id,
        CycleLog.start_date == cycle_in.start_date
    ).first()
    
    if existing_log:
        return existing_log

    # Find the most recent cycle that starts before this new date to compute the cycle length
    previous_cycle = db.query(CycleLog).filter(
        CycleLog.user_id == current_user.id,
        CycleLog.start_date < cycle_in.start_date
    ).order_by(CycleLog.start_date.desc()).first()

    cycle_length = None
    if previous_cycle:
        cycle_length = (cycle_in.start_date - previous_cycle.start_date).days

    new_cycle = CycleLog(
        user_id=current_user.id,
        start_date=cycle_in.start_date,
        cycle_length=cycle_length
    )
    
    db.add(new_cycle)
    db.commit()
    db.refresh(new_cycle)
    
    # Also update the subsequent cycle's length if we inserted a cycle in the middle of history
    next_cycle = db.query(CycleLog).filter(
        CycleLog.user_id == current_user.id,
        CycleLog.start_date > cycle_in.start_date
    ).order_by(CycleLog.start_date.asc()).first()
    
    if next_cycle:
        next_cycle.cycle_length = (next_cycle.start_date - cycle_in.start_date).days
        db.commit()

    return new_cycle

@router.put("/latest", response_model=CycleLogOut)
def update_latest_cycle_end(
    cycle_in: CycleLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log the end date of the active period bleeding to calculate active period length.
    """
    latest_cycle = db.query(CycleLog).filter(
        CycleLog.user_id == current_user.id
    ).order_by(CycleLog.start_date.desc()).first()

    if not latest_cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cycle logs found to update."
        )

    if cycle_in.end_date < latest_cycle.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period end date cannot be earlier than the start date."
        )

    latest_cycle.end_date = cycle_in.end_date
    latest_cycle.period_length = (cycle_in.end_date - latest_cycle.start_date).days + 1
    
    db.commit()
    db.refresh(latest_cycle)
    return latest_cycle

@router.get("", response_model=List[CycleLogOut])
def get_cycle_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve user cycle logs, ordered chronologically.
    """
    return db.query(CycleLog).filter(
        CycleLog.user_id == current_user.id
    ).order_by(CycleLog.start_date.desc()).all()

@router.get("/prediction", response_model=CyclePrediction)
def get_cycle_predictions_and_recs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate predicted next period date, days remaining, current cycle phase, and personalized recommendations.
    """
    latest_cycle = db.query(CycleLog).filter(
        CycleLog.user_id == current_user.id
    ).order_by(CycleLog.start_date.desc()).first()

    if not latest_cycle:
        # If no cycle has been logged, use today as baseline and standard 28-day cycle length
        today = date.today()
        avg_len = 28
        predicted_date = today + timedelta(days=28)
        current_phase = "Menstrual"
        recs = get_phase_recommendations(current_phase)
        return {
            "predicted_start_date": predicted_date,
            "days_until_next_period": 28,
            "current_phase": current_phase,
            "phase_recommendations": recs
        }

    # Fetch all cycles to calculate the custom average cycle length
    all_cycles = db.query(CycleLog).filter(
        CycleLog.user_id == current_user.id,
        CycleLog.cycle_length.isnot(None)
    ).all()

    if all_cycles:
        avg_len = int(sum(c.cycle_length for c in all_cycles) / len(all_cycles))
        # Keep within medically realistic limits (e.g. 21 to 90 days)
        avg_len = min(max(avg_len, 21), 90)
    else:
        avg_len = 28  # Clinical fallback default

    predicted_date = latest_cycle.start_date + timedelta(days=avg_len)
    today = date.today()
    days_until = (predicted_date - today).days

    # Current phase determination
    current_phase = get_cycle_phase(latest_cycle.start_date, today, avg_len)
    recs = get_phase_recommendations(current_phase)

    return {
        "predicted_start_date": predicted_date,
        "days_until_next_period": days_until,
        "current_phase": current_phase,
        "phase_recommendations": recs
    }
