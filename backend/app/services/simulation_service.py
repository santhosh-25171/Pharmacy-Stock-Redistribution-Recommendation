"""
Simulation and Baseline Evaluation Service.
Provides APIs to run or retrieve 30-scenario simulation results.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.evaluate import run_simulation_suite

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")
SIM_FILE = os.path.join(DATA_DIR, "simulation_results.json")

def get_latest_simulation_results() -> Dict[str, Any]:
    """Retrieves existing simulation evaluation or computes if missing."""
    if os.path.exists(SIM_FILE):
        try:
            with open(SIM_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    # Run simulation suite if not found
    return run_simulation_suite(num_scenarios=30)

def trigger_simulation_run(num_scenarios: int = 30) -> Dict[str, Any]:
    """Triggers on-demand re-execution of the simulation suite."""
    return run_simulation_suite(num_scenarios=num_scenarios)
