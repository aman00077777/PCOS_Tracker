from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Symptoms & Lifestyle Metrics
    pain_level = Column(Integer, default=0)       # 1-10 scale
    mood = Column(String, default="Calm")          # Calm, Happy, Irritable, Sad, Anxious
    bloating = Column(Integer, default=0)          # 0-3 (None, Mild, Moderate, Severe)
    hair_growth = Column(Integer, default=0)       # 0-3 (None, Mild, Moderate, Severe)
    acne = Column(Integer, default=0)              # 0-3 (None, Mild, Moderate, Severe)
    sleep_hours = Column(Float, default=8.0)
    diet_type = Column(String, default="Balanced")  # Balanced, Low Carb, High Sugar, Mediterranean, Keto
    exercise_minutes = Column(Integer, default=0)
    stress_level = Column(Integer, default=1)      # 1-10 scale
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="symptom_logs")

    # Enforce one log per user per day
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_daily_symptom"),
    )
