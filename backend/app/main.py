from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
# Import models to ensure they register on Base before create_all
from app.models import User, SymptomLog, CycleLog
from app.routers import auth, symptoms, cycles, predictions, alerts

# Initialize database schemas
print("[DB] Initializing database tables...")
Base.metadata.create_all(bind=engine)
print("[DB] Database initialization completed successfully.")

app = FastAPI(
    title="PCOS Tracker REST API",
    description="Backend services for PCOS symptom tracking, cycle predictions, ML analysis, and healthcare alerts.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API routers
app.include_router(auth.router)
app.include_router(symptoms.router)
app.include_router(cycles.router)
app.include_router(predictions.router)
app.include_router(alerts.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "PCOS Tracker API",
        "docs_url": "/docs"
    }
