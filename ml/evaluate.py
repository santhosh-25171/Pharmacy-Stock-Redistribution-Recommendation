"""
Simulation & Evaluation Engine.
Runs 30 reproducible multi-scenario simulations comparing:
1. Baseline Strategy (Local FIFO Clearance / Isolated Pharmacy Silos)
2. Proposed Expiry-Aware Redistribution Recommender (Demand & Transit Optimized)

Computes statistical metrics:
- Stock value used before expiry
- Stock value transferred before expiry
- Total value protected
- Stock value lost to expiry
- Acceptance, rejection, override rates
- Mean transit distance and shelf-life saved
"""

import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

def run_simulation_suite(num_scenarios=30, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    print(f"[*] Loading data for {num_scenarios}-scenario simulation...")
    inv_df = pd.read_csv(os.path.join(DATA_DIR, "synthetic_inventory.csv"))
    demand_df = pd.read_csv(os.path.join(DATA_DIR, "synthetic_demand.csv"))
    transfers_df = pd.read_csv(os.path.join(DATA_DIR, "synthetic_transfers.csv"))
    pharmacies_df = pd.read_csv(os.path.join(DATA_DIR, "synthetic_pharmacies.csv"))

    # Convert valid dates
    ref_date = datetime(2026, 8, 14)
    
    # Pre-build lookup tables
    demand_lookup = {(row["pharmacy_id"], row["medicine_id"]): row["daily_demand"] for _, row in demand_df.iterrows()}
    transfer_lookup = {(row["source_pharmacy_id"], row["destination_pharmacy_id"]): (row["distance_km"], row["estimated_transfer_days"], row["transfer_cost"]) for _, row in transfers_df.iterrows()}
    pharmacy_status = {row["pharmacy_id"]: row["operating_status"] for _, row in pharmacies_df.iterrows()}
    pharmacy_capacity = {row["pharmacy_id"]: row["storage_capacity"] for _, row in pharmacies_df.iterrows()}

    # Clean inventory for simulation
    valid_inv = []
    for _, row in inv_df.iterrows():
        try:
            exp = datetime.strptime(str(row["expiry_date"]), "%Y-%m-%d")
            dte = (exp - ref_date).days
            valid_inv.append({
                "inventory_id": row["inventory_id"],
                "medicine_id": row["medicine_id"],
                "medicine_name": row["medicine_name"],
                "pharmacy_id": row["pharmacy_id"],
                "quantity": int(row["quantity"]),
                "unit_price": float(row["unit_price"]),
                "expiry_date": row["expiry_date"],
                "days_to_expiry": dte,
                "stock_status": row["stock_status"],
                "edge_case_tag": row.get("edge_case_tag", "NONE")
            })
        except Exception:
            continue # Malformed dates handled as edge cases

    scenario_results = []

    for s_idx in range(1, num_scenarios + 1):
        # Scenario variations: demand shock multiplier between 0.8 and 1.35
        demand_mult = round(random.uniform(0.85, 1.25), 3)
        # Sample subset of ~400 near-expiry / available batches for each scenario cycle
        sample_batches = random.sample(valid_inv, min(450, len(valid_inv)))

        # === 1. BASELINE STRATEGY (Local FIFO, No Transfers) ===
        base_value_used = 0.0
        base_value_lost = 0.0

        for b in sample_batches:
            p_id = b["pharmacy_id"]
            m_id = b["medicine_id"]
            qty = b["quantity"]
            dte = b["days_to_expiry"]
            price = b["unit_price"]

            if pharmacy_status.get(p_id) != "ACTIVE" or dte <= 0:
                base_value_lost += qty * price
                continue

            local_daily = demand_lookup.get((p_id, m_id), 1.0) * demand_mult
            # In baseline, whatever cannot be consumed locally before expiry is wasted
            consumable = min(qty, int(local_daily * max(0, dte)))
            lost = max(0, qty - consumable)

            base_value_used += consumable * price
            base_value_lost += lost * price

        # === 2. PROPOSED EXPIRY-AWARE RECOMMENDER STRATEGY ===
        prop_value_used_local = 0.0
        prop_value_transferred = 0.0
        prop_value_lost = 0.0
        recommendations_count = 0
        accepted_count = 0
        rejected_count = 0
        overridden_count = 0
        distances = []
        shelf_lives_at_transfer = []

        active_pharmacies = [p for p, status in pharmacy_status.items() if status == "ACTIVE"]

        for b in sample_batches:
            p_src = b["pharmacy_id"]
            m_id = b["medicine_id"]
            qty = b["quantity"]
            dte = b["days_to_expiry"]
            price = b["unit_price"]
            edge_tag = b["edge_case_tag"]

            if pharmacy_status.get(p_src) != "ACTIVE" or dte <= 0 or edge_tag in ["ALREADY_EXPIRED", "INVALID_EXPIRY_DATE"]:
                prop_value_lost += qty * price
                continue

            local_daily = demand_lookup.get((p_src, m_id), 1.0) * demand_mult
            safety_stock = int(local_daily * 3) # 3 days safety stock
            consumable_local = min(qty, int(local_daily * max(0, dte)))
            excess = max(0, qty - consumable_local - safety_stock)

            prop_value_used_local += consumable_local * price
            remaining_unconsumed = qty - consumable_local

            if excess > 5 and dte >= 4 and edge_tag not in ["EXPIRES_BEFORE_TRANSIT", "NO_DESTINATION_DEMAND", "BELOW_SAFETY_STOCK"]:
                # Candidate destination search
                best_dest = None
                best_transfer_qty = 0
                best_score = -1

                for p_dest in active_pharmacies:
                    if p_dest == p_src:
                        continue

                    route_info = transfer_lookup.get((p_src, p_dest))
                    if not route_info:
                        continue
                    dist_km, transit_days, cost = route_info

                    # Safety Check: Must have remaining shelf life after transit
                    remaining_shelf_life = dte - transit_days
                    if remaining_shelf_life <= 2:
                        continue

                    dest_daily = demand_lookup.get((p_dest, m_id), 0.0) * demand_mult
                    if dest_daily <= 0.5:
                        continue

                    dest_capacity = pharmacy_capacity.get(p_dest, 5000)
                    dest_consumable_window = int(dest_daily * remaining_shelf_life)
                    
                    candidate_qty = min(excess, dest_consumable_window, int(dest_capacity * 0.15))

                    if candidate_qty >= 5:
                        # Scoring: high destination velocity, low distance, safe shelf-life
                        score = (dest_daily * 10) + (remaining_shelf_life * 2) - (dist_km * 0.3)
                        if score > best_score:
                            best_score = score
                            best_dest = p_dest
                            best_transfer_qty = candidate_qty
                            best_route = (dist_km, transit_days)

                if best_dest and best_transfer_qty > 0:
                    recommendations_count += 1
                    distances.append(best_route[0])
                    shelf_lives_at_transfer.append(dte - best_route[1])

                    # Simulate realistic pharmacist acceptance (92% accept, 5% reject, 3% override)
                    user_decision = random.choices(["APPROVE", "REJECT", "OVERRIDE"], weights=[0.92, 0.05, 0.03])[0]
                    if user_decision == "APPROVE":
                        accepted_count += 1
                        prop_value_transferred += best_transfer_qty * price
                        prop_value_lost += max(0, remaining_unconsumed - best_transfer_qty) * price
                    elif user_decision == "OVERRIDE":
                        overridden_count += 1
                        override_qty = int(best_transfer_qty * 0.7)
                        prop_value_transferred += override_qty * price
                        prop_value_lost += max(0, remaining_unconsumed - override_qty) * price
                    else:
                        rejected_count += 1
                        prop_value_lost += remaining_unconsumed * price
                else:
                    prop_value_lost += remaining_unconsumed * price
            else:
                prop_value_lost += remaining_unconsumed * price

        prop_total_protected = prop_value_used_local + prop_value_transferred
        improvement_val = prop_total_protected - base_value_used

        scenario_results.append({
            "scenario_id": f"SCENARIO-{s_idx:03d}",
            "demand_multiplier": demand_mult,
            "baseline_value_used": round(base_value_used, 2),
            "baseline_value_lost": round(base_value_lost, 2),
            "proposed_value_used_local": round(prop_value_used_local, 2),
            "proposed_value_transferred": round(prop_value_transferred, 2),
            "proposed_total_protected": round(prop_total_protected, 2),
            "proposed_value_lost": round(prop_value_lost, 2),
            "value_improvement": round(improvement_val, 2),
            "improvement_pct": round((improvement_val / max(1.0, base_value_used)) * 100, 2),
            "recommendations_count": recommendations_count,
            "accepted_count": accepted_count,
            "rejected_count": rejected_count,
            "overridden_count": overridden_count,
            "avg_transfer_distance_km": round(float(np.mean(distances)), 2) if distances else 0.0,
            "avg_remaining_shelf_life_days": round(float(np.mean(shelf_lives_at_transfer)), 2) if shelf_lives_at_transfer else 0.0
        })

    # Summary aggregations
    avg_base_used = float(np.mean([s["baseline_value_used"] for s in scenario_results]))
    avg_prop_protected = float(np.mean([s["proposed_total_protected"] for s in scenario_results]))
    avg_improvement = float(np.mean([s["value_improvement"] for s in scenario_results]))
    avg_improvement_pct = float(np.mean([s["improvement_pct"] for s in scenario_results]))
    avg_loss_reduction = float(np.mean([s["baseline_value_lost"] - s["proposed_value_lost"] for s in scenario_results]))
    total_recs = sum([s["recommendations_count"] for s in scenario_results])
    total_acc = sum([s["accepted_count"] for s in scenario_results])
    total_rej = sum([s["rejected_count"] for s in scenario_results])
    total_ovr = sum([s["overridden_count"] for s in scenario_results])

    overall_evaluation = {
        "num_scenarios": num_scenarios,
        "summary": {
            "baseline_avg_value_protected": round(avg_base_used, 2),
            "proposed_avg_value_protected": round(avg_prop_protected, 2),
            "average_monetary_improvement": round(avg_improvement, 2),
            "average_percentage_improvement": round(avg_improvement_pct, 2),
            "average_expiry_loss_reduction": round(avg_loss_reduction, 2),
            "total_recommendations_evaluated": total_recs,
            "overall_acceptance_rate_pct": round((total_acc / max(1, total_recs)) * 100, 2),
            "overall_rejection_rate_pct": round((total_rej / max(1, total_recs)) * 100, 2),
            "overall_override_rate_pct": round((total_ovr / max(1, total_recs)) * 100, 2),
            "overall_avg_transfer_distance_km": round(float(np.mean([s["avg_transfer_distance_km"] for s in scenario_results if s["avg_transfer_distance_km"] > 0])), 2),
            "overall_avg_remaining_shelf_life_days": round(float(np.mean([s["avg_remaining_shelf_life_days"] for s in scenario_results if s["avg_remaining_shelf_life_days"] > 0])), 2)
        },
        "scenarios": scenario_results
    }

    # Save to JSON
    sim_file = os.path.join(DATA_DIR, "simulation_results.json")
    with open(sim_file, "w", encoding="utf-8") as f:
        json.dump(overall_evaluation, f, indent=2)

    print(f"[+] Simulation Suite Complete: {num_scenarios} scenarios evaluated.")
    print(f"    - Baseline Avg Value Protected: INR {avg_base_used:,.2f}")
    print(f"    - Proposed Avg Value Protected: INR {avg_prop_protected:,.2f}")
    print(f"    - Mean Value Improvement:       INR {avg_improvement:,.2f} (+{avg_improvement_pct:.2f}%)")
    print(f"    - Loss Reduction:               INR {avg_loss_reduction:,.2f}")
    print(f"    - Overall Acceptance Rate:      {overall_evaluation['summary']['overall_acceptance_rate_pct']}%")
    print(f"[OK] Saved simulation results -> {sim_file}")

    return overall_evaluation

if __name__ == "__main__":
    run_simulation_suite()
