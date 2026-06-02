import pytest
from datetime import date, timedelta

# Test Case 1: User Signup and JWT Authentication
def test_user_auth(client):
    # 1. Signup
    signup_payload = {
        "email": "testuser@pcostracker.org",
        "password": "strongpassword123",
        "full_name": "Dr. Sarah"
    }
    response = client.post("/auth/signup", json=signup_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == signup_payload["email"]
    assert "id" in data
    
    # 2. Login
    login_payload = {
        "email": "testuser@pcostracker.org",
        "password": "strongpassword123"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

# Test Case 2: Daily Symptom Logging and Upsert Validation
def test_daily_symptoms_crud(client):
    # 1. Auth setup
    client.post("/auth/signup", json={
        "email": "symptomuser@pcostracker.org",
        "password": "mypassword123",
        "full_name": "Sarah P."
    })
    login_res = client.post("/auth/login", json={
        "email": "symptomuser@pcostracker.org",
        "password": "mypassword123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Log symptom for today
    today_str = str(date.today())
    symptom_payload = {
        "date": today_str,
        "pain_level": 5,
        "mood": "Calm",
        "bloating": 1,
        "hair_growth": 2,
        "acne": 1,
        "sleep_hours": 7.5,
        "diet_type": "Balanced",
        "exercise_minutes": 30,
        "stress_level": 4
    }
    response = client.post("/symptoms", json=symptom_payload, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["pain_level"] == 5
    assert res_data["mood"] == "Calm"

    # 3. Upsert: Update symptom for same date
    update_payload = symptom_payload.copy()
    update_payload["pain_level"] = 8
    update_payload["mood"] = "Fatigued"
    
    response = client.post("/symptoms", json=update_payload, headers=headers)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["pain_level"] == 8
    assert updated_data["mood"] == "Fatigued"

# Test Case 3: Menstrual Cycle prediction and Recommendations
def test_menstrual_cycle_prediction(client):
    # 1. Auth setup
    client.post("/auth/signup", json={
        "email": "cycleuser@pcostracker.org",
        "password": "mypassword123"
    })
    login_res = client.post("/auth/login", json={
        "email": "cycleuser@pcostracker.org",
        "password": "mypassword123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Log a start cycle (e.g. 28 days ago)
    start_date_1 = str(date.today() - timedelta(days=28))
    client.post("/cycles", json={"start_date": start_date_1}, headers=headers)

    # 3. Log a current start cycle today (creates an exact 28-day historical interval)
    start_date_2 = str(date.today())
    response = client.post("/cycles", json={"start_date": start_date_2}, headers=headers)
    assert response.status_code == 200
    
    # 4. Check predictions and personalized recommendations
    pred_res = client.get("/cycles/prediction", headers=headers)
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    
    assert "predicted_start_date" in pred_data
    assert pred_data["days_until_next_period"] == 28  # Based on 28-day calculated avg
    assert pred_data["current_phase"] == "Menstrual"  # Since today is day 1 of the new cycle
    assert "phase_recommendations" in pred_data

# Test Case 4: ML Inference API Simulation
def test_ml_inference(client):
    # 1. Auth setup
    client.post("/auth/signup", json={
        "email": "mluser@pcostracker.org",
        "password": "mypassword123"
    })
    login_res = client.post("/auth/login", json={
        "email": "mluser@pcostracker.org",
        "password": "mypassword123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test manual inference simulator endpoint
    params = {
        "sleep_hours": 5.5,
        "exercise_minutes": 10,
        "stress_level": 8.5,
        "pain_level": 6.0,
        "bloating": 2,
        "hair_growth": 3,
        "acne": 2,
        "diet_type": "High Sugar"
    }
    response = client.post("/predictions/predict", params=params, headers=headers)
    assert response.status_code == 200
    pred_data = response.json()
    assert "is_irregular" in pred_data
    assert "probability" in pred_data
    assert pred_data["probability"] > 0.50  # Should be high risk due to poor inputs

# Test Case 5: Alarm reminder Dispatch
def test_reminder_alerts(client):
    # 1. Auth setup
    client.post("/auth/signup", json={
        "email": "alertuser@pcostracker.org",
        "password": "mypassword123",
        "full_name": "Jane Doe"
    })
    login_res = client.post("/auth/login", json={
        "email": "alertuser@pcostracker.org",
        "password": "mypassword123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Fire medication reminder
    medication_payload = {
        "medication_name": "Metformin",
        "dosage": "500mg",
        "time": "With Breakfast",
        "notes": "Take with water",
        "email_recipient": "alertuser@pcostracker.org"
    }
    response = client.post("/alerts/medication", json=medication_payload, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "Notification request processed"
    assert "discord_sent" in res_data
    assert "email_sent" in res_data
