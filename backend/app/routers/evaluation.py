"""
Evaluation and Baseline Comparison Router.
Exposes results of 30-scenario simulations comparing naive baseline vs our proposed recommender.
"""

from fastapi import APIRouter, Depends
from backend.app.schemas import EvaluationOut
from backend.app.services.simulation_service import get_latest_simulation_results, trigger_simulation_run
from backend.app.services.ml_service import get_ml_metrics
from backend.app.utils.security import require_roles, get_current_user
from backend.app.models import User

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])

@router.get("", response_model=EvaluationOut)
def get_evaluation_data():
    sim_data = get_latest_simulation_results()
    ml_data = get_ml_metrics()
    
    return EvaluationOut(
        num_scenarios=sim_data.get("num_scenarios", 30),
        summary=sim_data.get("summary", {}),
        scenarios=sim_data.get("scenarios", []),
        ml_metrics=ml_data
    )

@router.post("/run", response_model=EvaluationOut)
def run_evaluation(current_user: User = Depends(require_roles(["ADMIN", "MANAGER"]))):
    """Triggers live execution of the 30-scenario simulation suite."""
    sim_data = trigger_simulation_run(num_scenarios=30)
    ml_data = get_ml_metrics()

    return EvaluationOut(
        num_scenarios=sim_data.get("num_scenarios", 30),
        summary=sim_data.get("summary", {}),
        scenarios=sim_data.get("scenarios", []),
        ml_metrics=ml_data
    )
