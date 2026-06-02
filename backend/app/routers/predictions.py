from datetime import date, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.symptom import SymptomLog
from app.routers.auth import get_current_user
from app.services.ml_model import ml_model_service

router = APIRouter(prefix="/predictions", tags=["ML Predictions"])

DIET_MAP = {
    "Low Carb": 0,
    "Mediterranean": 1,
    "Balanced": 2,
    "Keto": 3,
    "High Sugar": 4
}

@router.post("/predict")
def predict_cycle_irregularity(
    sleep_hours: float,
    exercise_minutes: int,
    stress_level: float,
    pain_level: float,
    bloating: int,
    hair_growth: int,
    acne: int,
    diet_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    Direct endpoint to predict menstrual cycle irregularity based on individual lifestyle inputs.
    """
    diet_num = DIET_MAP.get(diet_type, 2)  # Default to Balanced (2)
    
    result = ml_model_service.predict_irregularity(
        sleep_hours=sleep_hours,
        exercise_minutes=exercise_minutes,
        stress_level=stress_level,
        pain_level=pain_level,
        bloating=float(bloating),
        hair_growth=float(hair_growth),
        acne=float(acne),
        diet_type=diet_num
    )
    return result

@router.get("/analyze-my-lifestyle")
def analyze_logged_lifestyle(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyzes the user's logged symptoms over the last N days, computes averages, and predicts cycle irregularity.
    """
    cutoff_date = date.today() - timedelta(days=days)
    
    # Query logs in date range
    logs = db.query(SymptomLog).filter(
        SymptomLog.user_id == current_user.id,
        SymptomLog.date >= cutoff_date
    ).all()
    
    if not logs:
        return {
            "has_enough_data": False,
            "message": f"You haven't logged any symptoms in the last {days} days. Log daily symptoms to run ML analysis.",
            "averages": {},
            "prediction": {}
        }
        
    # Compute averages
    total_logs = len(logs)
    avg_sleep = sum(l.sleep_hours for l in logs) / total_logs
    avg_exercise = sum(l.exercise_minutes for l in logs) / total_logs
    avg_stress = sum(l.stress_level for l in logs) / total_logs
    avg_pain = sum(l.pain_level for l in logs) / total_logs
    avg_bloating = sum(l.bloating for l in logs) / total_logs
    avg_hair = sum(l.hair_growth for l in logs) / total_logs
    avg_acne = sum(l.acne for l in logs) / total_logs
    
    # Diet mode calculation
    diet_counts = {}
    for l in logs:
        diet_counts[l.diet_type] = diet_counts.get(l.diet_type, 0) + 1
    most_common_diet = max(diet_counts, key=diet_counts.get) if diet_counts else "Balanced"
    diet_num = DIET_MAP.get(most_common_diet, 2)
    
    prediction = ml_model_service.predict_irregularity(
        sleep_hours=avg_sleep,
        exercise_minutes=int(avg_exercise),
        stress_level=avg_stress,
        pain_level=avg_pain,
        bloating=avg_bloating,
        hair_growth=avg_hair,
        acne=avg_acne,
        diet_type=diet_num
    )
    
    return {
        "has_enough_data": True,
        "total_days_logged": total_logs,
        "averages": {
            "sleep_hours": round(avg_sleep, 2),
            "exercise_minutes": round(avg_exercise, 1),
            "stress_level": round(avg_stress, 2),
            "pain_level": round(avg_pain, 2),
            "bloating": round(avg_bloating, 2),
            "hair_growth": round(avg_hair, 2),
            "acne": round(avg_acne, 2),
            "diet_type": most_common_diet
        },
        "prediction": prediction
    }
