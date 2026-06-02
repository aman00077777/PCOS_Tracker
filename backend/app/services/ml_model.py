import os
import joblib
import pandas as pd
from typing import Dict, Any
from app.config import settings

class MLModelService:
    def __init__(self):
        self.model = None
        self.model_path = settings.MODEL_PATH
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"[ML MODEL] Loaded successfully from {self.model_path}")
            except Exception as e:
                print(f"[ML MODEL ERROR] Failed to load model. Exception: {str(e)}")
                self.model = None
        else:
            print(f"[ML MODEL WARNING] Checkpoint not found at {self.model_path}. Running with fallback heuristics.")
            self.model = None

    def predict_irregularity(
        self,
        sleep_hours: float,
        exercise_minutes: int,
        stress_level: float,
        pain_level: float,
        bloating: float,
        hair_growth: float,
        acne: float,
        diet_type: int
    ) -> Dict[str, Any]:
        """
        Predicts the probability of cycle irregularity based on patient inputs.
        """
        # If model is loaded, use it for inference
        if self.model is not None:
            try:
                # Features list ordered exactly as generated in training
                features = pd.DataFrame([{
                    "sleep_hours": sleep_hours,
                    "exercise_minutes": exercise_minutes,
                    "stress_level": stress_level,
                    "pain_level": pain_level,
                    "bloating": bloating,
                    "hair_growth": hair_growth,
                    "acne": acne,
                    "diet_type": diet_type
                }])
                
                prediction = int(self.model.predict(features)[0])
                probabilities = self.model.predict_proba(features)[0]
                irregularity_prob = float(probabilities[1])
                
                return {
                    "is_irregular": prediction == 1,
                    "probability": irregularity_prob,
                    "method": "Random Forest ML Model"
                }
            except Exception as e:
                print(f"[ML INFERENCE ERROR] {str(e)}. Falling back to heuristics.")
        
        # Fallback Heuristics if ML model is unavailable or throws error
        # High androgen (hair, acne), high stress, low sleep, sugar diet increase risk
        score = 0.15
        if sleep_hours < 6.5:
            score += 0.15
        if exercise_minutes < 25:
            score += 0.15
        if stress_level > 7.0:
            score += 0.10
        if diet_type == 4: # High Sugar
            score += 0.10
        if hair_growth > 1.8:
            score += 0.15
        if acne > 1.8:
            score += 0.10
            
        prob = min(max(score, 0.05), 0.95)
        return {
            "is_irregular": prob >= 0.50,
            "probability": prob,
            "method": "Clinical Heuristic Rules Engine (Fallback)"
        }

# Singleton instance
ml_model_service = MLModelService()
