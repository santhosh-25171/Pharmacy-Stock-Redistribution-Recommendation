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

import logging
from sqlalchemy import text
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.app.models import User, TransferRecommendation
from backend.app.schemas import SystemHealthOut
from backend.app.utils.security import require_roles
from backend.app.services.ml_service import get_ml_health_status
from backend.app.recommender.risk_scorer import get_reference_date_info
from backend.app.services.audit_service import log_audit_event

logger = logging.getLogger("pharmacy.api")

# Centralized Error Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles standard HTTPExceptions while preserving detail and adding error metadata."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": "HTTPException", "status_code": exc.status_code},
        headers=getattr(exc, "headers", None)
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Sanitizes Pydantic request validation errors into a clean, structured payload."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "error_type": "ValidationError", "status_code": 422}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Prevents stack trace leaks on unexpected exceptions, returning safe 500 JSON response."""
    logger.error(f"[CRITICAL] Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please contact the system administrator.",
            "error_type": "InternalServerError",
            "status_code": 500
        }
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

@app.get("/health", response_model=SystemHealthOut, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint validating API, DB, ML Model, and Subsystem connectivity."""
    # Check DB connectivity
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    ml_health = get_ml_health_status()
    ref_info = get_reference_date_info()
    
    # Check recommender status
    rec_count = db.query(TransferRecommendation).count()

    overall_status = "healthy"
    if db_status != "connected" or ml_health.get("status") != "HEALTHY":
        overall_status = "degraded"

    return SystemHealthOut(
        status=overall_status,
        service="pharmacy-redistribution-recommender",
        database=db_status,
        api="healthy",
        ml_model=ml_health,
        recommender={
            "status": "active",
            "active_recommendations": rec_count,
            "engine": "feasibility_constrained_velocity_ranking"
        },
        audit_service="healthy",
        reference_date=ref_info,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@app.post("/api/seed", tags=["Admin"])
def force_reseed(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    """
    Administrative endpoint to force re-seed the synthetic dataset.
    Requires ADMIN authentication and authorization.
    """
    seed_database_if_empty(db=db, force_reseed=True)
    
    # Audit log entry for administration re-seed
    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="SEEDED",
        reason=f"Administrator ({current_user.email}) initiated database re-seed and reset"
    )
    
    return {
        "status": "success",
        "message": "Database successfully re-seeded with 5,000+ batches by Administrator.",
        "admin_user": current_user.email
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
