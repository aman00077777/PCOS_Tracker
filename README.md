# PCOS Tracker

> A comprehensive, full-stack Polycystic Ovary Syndrome (PCOS) health tracking and lifestyle analytics platform.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?style=flat-square&logo=scikit-learn)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## Live Demo

| Service | URL |
|---|---|
| Streamlit Dashboard | https://pcos-tracker-frontend.onrender.com |
| FastAPI Backend | https://pcos-tracker-szsh.onrender.com |
| API Documentation | https://pcos-tracker-szsh.onrender.com/docs |

> Note: Hosted on Render free tier — services may take 30–60 seconds to wake up on first visit.

---

## Overview

PCOS affects approximately 1 in 5 women globally. Most period trackers on the market are generic and fail to address PCOS-specific symptoms such as insulin resistance, hirsutism, acne, pelvic pain, sleep deficiency, and chronic cycle irregularity.

PCOS Tracker is a full-stack medical-grade web application designed specifically for individuals managing PCOS. It combines daily symptom logging, menstrual cycle tracking, machine learning-based irregularity prediction, and personalized phase-specific lifestyle recommendations into a single, unified platform.

---

## Key Features

| Feature | Description |
|---|---|
| Secure Authentication | JWT token-based auth with email/password and Google OAuth Single Sign-On |
| Daily Symptom Tracker | Log pelvic pain, mood, sleep hours, exercise, stress index, diet type, bloating, hirsutism, and acne severity |
| Menstrual Cycle Tracker | Record cycle histories, compute average cycle lengths, track bleeding days, and predict future periods |
| ML Irregularity Predictor | Random Forest Classifier trained on 30-day lifestyle metrics to project cycle irregularity probability with scenario simulation |
| Phase-Specific Recommendations | Dynamic lifestyle, nutritional, and exercise guidance per cycle phase (Menstrual, Follicular, Ovulatory, Luteal) |
| Medication & Appointment Alerts | Automated reminders via Discord Webhook and secure SMTP email notifications |
| Visual Analytics Dashboard | Interactive Plotly charts for cycle length variance tracking and symptom correlation heatmaps |
| PDF & CSV Export | Download raw data as CSV or generate a structured clinical PDF report for healthcare providers |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI, Python 3.10+, SQLAlchemy ORM, Uvicorn |
| Frontend | Streamlit, Plotly, Custom HTML/CSS Components |
| Database | PostgreSQL (Supabase — production), SQLite (local fallback) |
| Machine Learning | scikit-learn (Random Forest Classifier), joblib, pandas |
| Authentication | JWT (python-jose), bcrypt (passlib), Google OAuth |
| Notifications | Discord Webhooks, SMTP (Gmail / custom mail servers) |
| Report Generation | fpdf2 (lightweight vector PDF rendering) |
| Testing | pytest, httpx, pytest-asyncio |
| Deployment | Docker, Docker Compose, Render.com |
| CI/CD | GitHub Actions (automated weekly model retraining) |

---

## Project Architecture

```
PCOS Tracker/
├── backend/
│   ├── app/
│   │   ├── models/             # SQLAlchemy database ORM definitions
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── routers/            # API route handlers (auth, symptoms, cycles, alerts, predictions)
│   │   ├── services/           # ML inference, alert dispatch, recommendation engine
│   │   ├── tests/              # Automated pytest test suite
│   │   ├── config.py           # Application settings and environment parser
│   │   ├── database.py         # Database engine with PostgreSQL/SQLite failover
│   │   └── main.py             # FastAPI application entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── .streamlit/
│   │   └── config.toml         # Streamlit theme configuration
│   ├── app.py                  # Streamlit application source
│   ├── report_generator.py     # PDF clinical report generator
│   ├── requirements.txt
│   └── Dockerfile
├── ml/
│   ├── data/                   # Training datasets
│   ├── models/                 # Serialized model weights (.pkl)
│   ├── generate_data.py        # Synthetic PCOS data generator
│   └── train.py                # Random Forest training pipeline
├── .github/
│   └── workflows/
│       └── retrain.yml         # Weekly automated model retraining (CI/CD)
├── docker-compose.yml          # Multi-container orchestration
└── README.md
```

---

## Getting Started

### Method 1: Docker (Recommended)

Launch the full stack — backend, frontend, and database — with a single command:

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Streamlit Dashboard | http://localhost:8501 |
| FastAPI Interactive Docs | http://localhost:8000/docs |

### Method 2: Local Installation

**1. Backend Setup**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. Train the ML Model**
```bash
python ml/generate_data.py
python ml/train.py
```

This generates synthetic PCOS-correlated data and writes the trained model to `ml/models/pcos_rf_model.pkl`.

**3. Frontend Setup**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
# Database (falls back to SQLite if omitted)
DATABASE_URL=postgresql://user:password@host:port/dbname

# JWT Authentication
SECRET_KEY=your_secure_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Discord Notifications (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Email Notifications / SMTP (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
MAIL_FROM=noreply@pcostracker.org
```

> All alert integrations are optional. The application runs fully without Discord or SMTP configured.

---

## Running Tests

```bash
set PYTHONPATH=backend
python -m pytest backend/app/tests -v
```

Covers authentication, symptom logging, cycle tracking, ML predictions, and alert dispatching.

---

## Deployment

### Database — Supabase (Free Tier)

1. Create a free project at [supabase.com](https://supabase.com)
2. Navigate to **Settings → Database**
3. Copy the **PostgreSQL connection URI**
4. Set it as `DATABASE_URL` in your deployment environment

### Application — Render.com

**Backend (FastAPI)**
- New Web Service → connect GitHub repo
- Root Directory: `backend`
- Runtime: `Docker`
- Environment Variables: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`

**Frontend (Streamlit)**
- New Web Service → connect GitHub repo
- Root Directory: `frontend`
- Runtime: `Docker`
- Environment Variables: `BACKEND_URL` = your deployed FastAPI URL

### CI/CD — Automated Model Retraining

A GitHub Actions workflow (`.github/workflows/retrain.yml`) runs weekly to:
- Generate fresh synthetic training data
- Retrain the Random Forest Classifier
- Commit updated model weights back to the repository

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user account |
| POST | `/auth/login` | Authenticate and receive JWT token |
| POST | `/auth/google` | Google OAuth authentication |
| GET | `/symptoms` | Retrieve logged symptoms |
| POST | `/symptoms` | Log daily symptom entry |
| GET | `/cycles` | Retrieve cycle history |
| POST | `/cycles` | Log a new menstrual cycle |
| PUT | `/cycles/latest` | Update the latest active cycle |
| GET | `/cycles/prediction` | Get next period prediction |
| POST | `/predictions/predict` | Run ML irregularity prediction |
| GET | `/predictions/analyze-my-lifestyle` | 30-day lifestyle analysis |
| POST | `/alerts/medication` | Dispatch medication reminder |
| POST | `/alerts/appointment` | Dispatch appointment reminder |
| POST | `/alerts/test-discord` | Test Discord webhook |
| POST | `/alerts/test-email` | Test email notification |
| GET | `/recommendations` | Get phase-specific recommendations |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

Made by **Aman Sharma** — [github.com/aman00077777](https://github.com/aman00077777)