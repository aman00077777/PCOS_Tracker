import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def train_model():
    data_path = "ml/data/pcos_synthetic_data.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Synthetic dataset not found at {data_path}. Please run generate_data.py first.")
        
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Features & Target
    X = df.drop(columns=["irregular"])
    y = df["irregular"]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier model...")
    # Initialize Random Forest with balanced class weight to address any skew
    clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, class_weight="balanced")
    clf.fit(X_train, y_train)
    
    # Evaluate
    predictions = clf.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    print(f"Model Training Complete.")
    print(f"Test Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))
    
    # Save the model
    os.makedirs("ml/models", exist_ok=True)
    model_save_path = "ml/models/pcos_rf_model.pkl"
    joblib.dump(clf, model_save_path)
    print(f"Model saved successfully to {model_save_path}")

if __name__ == "__main__":
    train_model()
