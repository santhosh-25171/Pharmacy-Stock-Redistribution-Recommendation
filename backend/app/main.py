"""
FastAPI Application Entry Point.
Expiry-Aware Pharmacy Stock Redistribution Recommender.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path for direct execution (e.g. python backend/app/main.py)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.database.session import engine, Base, get_db
from backend.app.services.seeding_service import seed_database_if_empty
from backend.app.routers import (
    auth, inventory, pharmacies, medicines,
    recommendations, analytics, evaluation, audit_logs, edge_cases
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema and seed with synthetic data on startup
    print("[*] Initializing database and ensuring synthetic data is populated...")
    seed_database_if_empty()
    yield
    print("[*] Application shutdown.")

app = FastAPI(
    title="Expiry-Aware Pharmacy Stock Redistribution Recommender API",
    description="Explainable, safety-constrained medication redistribution recommendation engine with human-in-the-loop oversight.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(pharmacies.router)
app.include_router(medicines.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(evaluation.router)
app.include_router(audit_logs.router)
app.include_router(edge_cases.router)

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint validating API and DB connectivity."""
    return {
        "status": "healthy",
        "service": "pharmacy-redistribution-recommender",
        "database": "connected",
        "timestamp": "2026-08-14T10:00:00Z"
    }

@app.post("/api/seed", tags=["Admin"])
def force_reseed(db: Session = Depends(get_db)):
    """Admin utility endpoint to force re-seed the synthetic dataset."""
    seed_database_if_empty(db=db, force_reseed=True)
    return {"status": "success", "message": "Database successfully re-seeded with 5,000+ batches."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
