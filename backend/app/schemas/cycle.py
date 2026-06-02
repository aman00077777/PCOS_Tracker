from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List, Dict, Any

class CycleLogBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None

class CycleLogCreate(BaseModel):
    start_date: date

class CycleLogUpdate(BaseModel):
    end_date: date

class CycleLogOut(CycleLogBase):
    id: int
    user_id: int
    cycle_length: Optional[int] = None
    period_length: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CyclePrediction(BaseModel):
    predicted_start_date: date
    days_until_next_period: int
    current_phase: str
    phase_recommendations: Dict[str, Any]
