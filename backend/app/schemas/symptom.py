from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class SymptomLogBase(BaseModel):
    date: date
    pain_level: int = Field(default=0, ge=0, le=10, description="Pain rating from 0 to 10")
    mood: str = Field(default="Calm", description="Current emotional state")
    bloating: int = Field(default=0, ge=0, le=3, description="Bloating level (0: None, 1: Mild, 2: Moderate, 3: Severe)")
    hair_growth: int = Field(default=0, ge=0, le=3, description="Excessive hair growth/hirsutism rating (0: None, 1: Mild, 2: Moderate, 3: Severe)")
    acne: int = Field(default=0, ge=0, le=3, description="Acne breakout rating (0: None, 1: Mild, 2: Moderate, 3: Severe)")
    sleep_hours: float = Field(default=8.0, ge=0.0, le=24.0, description="Hours of sleep received")
    diet_type: str = Field(default="Balanced", description="Type of diet consumed (Balanced, Low Carb, High Sugar, Mediterranean, Keto)")
    exercise_minutes: int = Field(default=0, ge=0, le=1440, description="Exercise duration in minutes")
    stress_level: int = Field(default=1, ge=1, le=10, description="Stress rating from 1 to 10")

class SymptomLogCreate(SymptomLogBase):
    pass

class SymptomLogOut(SymptomLogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
