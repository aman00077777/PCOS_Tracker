import os
import pandas as pd
import numpy as np

def generate_pcos_dataset(n_samples=1000, random_seed=42):
    np.random.seed(random_seed)
    
    # Lifestyle and Symptom features
    sleep_hours = np.random.uniform(5.0, 9.5, n_samples)
    exercise_minutes = np.random.randint(0, 90, n_samples)
    stress_level = np.random.uniform(1.0, 10.0, n_samples)
    pain_level = np.random.uniform(0.0, 10.0, n_samples)
    bloating = np.random.uniform(0.0, 3.0, n_samples)
    hair_growth = np.random.uniform(0.0, 3.0, n_samples)
    acne = np.random.uniform(0.0, 3.0, n_samples)
    
    # Diet type mapped to numerical value for ML training
    # 0: Low Carb, 1: Mediterranean, 2: Balanced, 3: Keto, 4: High Sugar
    diet_mapped = np.random.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.2, 0.2, 0.3, 0.1, 0.2])
    
    # Probability of cycle irregularity based on clinical logic:
    # High stress, poor sleep (<7h), lack of exercise (<20m), high sugar diet (4), high acne & hair growth
    # (PCOS symptoms are driven by insulin resistance and androgen excess)
    prob = (
        0.15 
        + 0.15 * (sleep_hours < 6.5) 
        + 0.15 * (exercise_minutes < 25)
        + 0.10 * (stress_level > 7.0)
        + 0.10 * (diet_mapped == 4)  # High Sugar
        + 0.15 * (hair_growth > 1.8)  # Hirsutism correlation
        + 0.10 * (acne > 1.8)         # Acne correlation
    )
    
    # Clip probability between 0 and 1
    prob = np.clip(prob, 0.0, 0.95)
    
    # Irregular target: 1 = Irregular, 0 = Regular
    irregular = np.random.binomial(1, prob)
    
    df = pd.DataFrame({
        "sleep_hours": np.round(sleep_hours, 1),
        "exercise_minutes": exercise_minutes,
        "stress_level": np.round(stress_level, 1),
        "pain_level": np.round(pain_level, 1),
        "bloating": np.round(bloating, 1),
        "hair_growth": np.round(hair_growth, 1),
        "acne": np.round(acne, 1),
        "diet_type": diet_mapped,
        "irregular": irregular
    })
    
    return df

if __name__ == "__main__":
    print("Generating synthetic PCOS tracker dataset...")
    df = generate_pcos_dataset(1500)
    
    # Create directory if it doesn't exist
    os.makedirs("ml/data", exist_ok=True)
    df.to_csv("ml/data/pcos_synthetic_data.csv", index=False)
    print(f"Dataset saved successfully. Shape: {df.shape}")
    print(df["irregular"].value_counts(normalize=True))
