"""
Synthetic Dataset Generator for Expiry-Aware Pharmacy Stock Redistribution Recommender.
Generates realistic data for:
- Pharmacies (locations, capacity, operating status)
- Medicines (names, categories, unit prices, storage types, critical flags)
- Inventory Batches (5,000+ batches, expiry dates, quantities, received dates, stock status, edge cases)
- Demand Forecasts (daily, weekly, monthly demand, trends)
- Inter-pharmacy Transfer Matrix (distances, estimated transit days, transfer costs)

NOTE: ALL DATA IS 100% SYNTHETIC FOR RESEARCH AND PROTOTYPING. NO PII OR REAL PATIENT DATA.
"""

import os
import random
import csv
from datetime import datetime, timedelta

# Fix random seed for reproducibility
random.seed(42)

# Determine data dir relative to script location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in locals() else os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 18 Realistic Synthetic Pharmacy Locations across major metropolitan zones
PHARMACIES = [
    {"pharmacy_id": "PHARM-001", "pharmacy_name": "Apollo Central Hub", "city": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946, "storage_capacity": 15000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-002", "pharmacy_name": "MedPlus Indiranagar", "city": "Bengaluru", "latitude": 12.9784, "longitude": 77.6408, "storage_capacity": 8000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-003", "pharmacy_name": "Fortis Care Pharmacy", "city": "Bengaluru", "latitude": 12.9352, "longitude": 77.6245, "storage_capacity": 10000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-004", "pharmacy_name": "Manipal Health Dispensary", "city": "Bengaluru", "latitude": 12.9915, "longitude": 77.5712, "storage_capacity": 12000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-005", "pharmacy_name": "TrustMed Koramangala", "city": "Bengaluru", "latitude": 12.9279, "longitude": 77.6271, "storage_capacity": 6500, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-006", "pharmacy_name": "Aster CMI Pharmacy", "city": "Bengaluru", "latitude": 13.0601, "longitude": 77.5925, "storage_capacity": 9000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-007", "pharmacy_name": "Whitefield Wellness Chemist", "city": "Bengaluru", "latitude": 12.9698, "longitude": 77.7500, "storage_capacity": 7500, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-008", "pharmacy_name": "Columbia Care Clinic Pharmacy", "city": "Bengaluru", "latitude": 13.0112, "longitude": 77.5550, "storage_capacity": 8500, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-009", "pharmacy_name": "Electronic City MedStore", "city": "Bengaluru", "latitude": 12.8452, "longitude": 77.6602, "storage_capacity": 7000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-010", "pharmacy_name": "Yelahanka Suburban Care", "city": "Bengaluru", "latitude": 13.1007, "longitude": 77.5963, "storage_capacity": 5500, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-011", "pharmacy_name": "Narayana Health Point", "city": "Bengaluru", "latitude": 12.8090, "longitude": 77.6947, "storage_capacity": 11000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-012", "pharmacy_name": "Malleshwaram Life Pharmacy", "city": "Bengaluru", "latitude": 13.0031, "longitude": 77.5643, "storage_capacity": 6000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-013", "pharmacy_name": "Jayanagar Community Chemist", "city": "Bengaluru", "latitude": 12.9250, "longitude": 77.5838, "storage_capacity": 7200, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-014", "pharmacy_name": "Hebbal Rapid Meds", "city": "Bengaluru", "latitude": 13.0358, "longitude": 77.5970, "storage_capacity": 6800, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-015", "pharmacy_name": "HSR Layout QuickPharma", "city": "Bengaluru", "latitude": 12.9121, "longitude": 77.6446, "storage_capacity": 8200, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-016", "pharmacy_name": "BTM Layout PharmaCare", "city": "Bengaluru", "latitude": 12.9166, "longitude": 77.6101, "storage_capacity": 5000, "operating_status": "ACTIVE"},
    {"pharmacy_id": "PHARM-017", "pharmacy_name": "Rajajinagar Health Haven", "city": "Bengaluru", "latitude": 12.9982, "longitude": 77.5530, "storage_capacity": 4500, "operating_status": "MAINTENANCE"}, # Edge case: Maintenance
    {"pharmacy_id": "PHARM-018", "pharmacy_name": "Peenya Industrial Dispensary", "city": "Bengaluru", "latitude": 13.0285, "longitude": 77.5197, "storage_capacity": 4000, "operating_status": "CLOSED"}, # Edge case: Closed
]

# 60 Synthetic Medicines across critical categories
MEDICINES = [
    {"medicine_id": "MED-001", "name": "Paracetamol 650mg", "category": "Analgesic", "unit_price": 32.50, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-002", "name": "Amoxicillin + Clavulanate 625mg", "category": "Antibiotic", "unit_price": 185.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-003", "name": "Azithromycin 500mg", "category": "Antibiotic", "unit_price": 120.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-004", "name": "Metformin 500mg SR", "category": "Antidiabetic", "unit_price": 45.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-005", "name": "Human Regular Insulin 100IU", "category": "Antidiabetic", "unit_price": 350.00, "is_critical": True, "storage_type": "Cold Chain 2-8C"},
    {"medicine_id": "MED-006", "name": "Atorvastatin 20mg", "category": "Cardiovascular", "unit_price": 95.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-007", "name": "Telmisartan 40mg", "category": "Cardiovascular", "unit_price": 78.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-008", "name": "Amlodipine 5mg", "category": "Cardiovascular", "unit_price": 38.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-009", "name": "Pantoprazole 40mg", "category": "Gastrointestinal", "unit_price": 85.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-010", "name": "Omeprazole 20mg", "category": "Gastrointestinal", "unit_price": 55.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-011", "name": "Cefixime 200mg", "category": "Antibiotic", "unit_price": 140.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-012", "name": "Ciprofloxacin 500mg", "category": "Antibiotic", "unit_price": 65.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-013", "name": "Montelukast + Levocetirizine", "category": "Respiratory", "unit_price": 115.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-014", "name": "Salbutamol Inhaler 100mcg", "category": "Respiratory", "unit_price": 160.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-015", "name": "Budesonide Inhaler 200mcg", "category": "Respiratory", "unit_price": 280.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-016", "name": "Ibuprofen 400mg", "category": "Analgesic", "unit_price": 28.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-017", "name": "Tramadol 50mg", "category": "Analgesic", "unit_price": 90.00, "is_critical": True, "storage_type": "Controlled Substance"},
    {"medicine_id": "MED-018", "name": "Enoxaparin 40mg Injection", "category": "Cardiovascular", "unit_price": 450.00, "is_critical": True, "storage_type": "Cold Chain 2-8C"},
    {"medicine_id": "MED-019", "name": "Meropenem 1g Injection", "category": "Antibiotic", "unit_price": 850.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-020", "name": "Piperacillin + Tazobactam 4.5g", "category": "Antibiotic", "unit_price": 490.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-021", "name": "Losartan 50mg", "category": "Cardiovascular", "unit_price": 62.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-022", "name": "Glimepiride 2mg", "category": "Antidiabetic", "unit_price": 52.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-023", "name": "Vildagliptin 50mg", "category": "Antidiabetic", "unit_price": 175.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-024", "name": "Dapagliflozin 10mg", "category": "Antidiabetic", "unit_price": 220.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-025", "name": "Rosuvastatin 10mg", "category": "Cardiovascular", "unit_price": 110.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-026", "name": "Clopidogrel 75mg", "category": "Cardiovascular", "unit_price": 88.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-027", "name": "Aspirin 75mg Gastro-resistant", "category": "Cardiovascular", "unit_price": 22.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-028", "name": "Ondansetron 4mg", "category": "Gastrointestinal", "unit_price": 42.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-029", "name": "Rabeprazole 20mg", "category": "Gastrointestinal", "unit_price": 75.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-030", "name": "Doxycycline 100mg", "category": "Antibiotic", "unit_price": 68.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-031", "name": "Levofloxacin 500mg", "category": "Antibiotic", "unit_price": 95.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-032", "name": "Linezolid 600mg", "category": "Antibiotic", "unit_price": 340.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-033", "name": "Vancomycin 500mg Injection", "category": "Antibiotic", "unit_price": 420.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-034", "name": "Methylprednisolone 16mg", "category": "Steroid", "unit_price": 110.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-035", "name": "Dexamethasone 4mg Injection", "category": "Steroid", "unit_price": 25.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-036", "name": "Prednisolone 10mg", "category": "Steroid", "unit_price": 30.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-037", "name": "Cetirizine 10mg", "category": "Antihistamine", "unit_price": 20.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-038", "name": "Fexofenadine 120mg", "category": "Antihistamine", "unit_price": 82.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-039", "name": "Hydrochlorothiazide 12.5mg", "category": "Cardiovascular", "unit_price": 24.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-040", "name": "Spironolactone 25mg", "category": "Cardiovascular", "unit_price": 48.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-041", "name": "Alprazolam 0.5mg", "category": "Psychiatric", "unit_price": 35.00, "is_critical": False, "storage_type": "Controlled Substance"},
    {"medicine_id": "MED-042", "name": "Escitalopram 10mg", "category": "Psychiatric", "unit_price": 85.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-043", "name": "Sertraline 50mg", "category": "Psychiatric", "unit_price": 105.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-044", "name": "Thyroxine Sodium 50mcg", "category": "Endocrine", "unit_price": 125.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-045", "name": "Calcium 500mg + Vitamin D3", "category": "Nutritional", "unit_price": 65.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-046", "name": "Vitamin B-Complex + B12", "category": "Nutritional", "unit_price": 40.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-047", "name": "Iron + Folic Acid Tablets", "category": "Nutritional", "unit_price": 50.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-048", "name": "Diclofenac Sodium 50mg", "category": "Analgesic", "unit_price": 30.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-049", "name": "Aceclofenac + Paracetamol", "category": "Analgesic", "unit_price": 60.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-050", "name": "Loperamide 2mg", "category": "Gastrointestinal", "unit_price": 18.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-051", "name": "Metronidazole 400mg", "category": "Antibiotic", "unit_price": 32.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-052", "name": "Fluconazole 150mg", "category": "Antifungal", "unit_price": 45.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-053", "name": "Itraconazole 100mg", "category": "Antifungal", "unit_price": 165.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-054", "name": "Ranitidine 150mg", "category": "Gastrointestinal", "unit_price": 25.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-055", "name": "Betamethasone 0.5mg", "category": "Steroid", "unit_price": 15.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-056", "name": "Bisoprolol 2.5mg", "category": "Cardiovascular", "unit_price": 72.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-057", "name": "Carvedilol 6.25mg", "category": "Cardiovascular", "unit_price": 54.00, "is_critical": False, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-058", "name": "Sitagliptin 100mg", "category": "Antidiabetic", "unit_price": 240.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-059", "name": "Empagliflozin 25mg", "category": "Antidiabetic", "unit_price": 290.00, "is_critical": True, "storage_type": "Room Temperature"},
    {"medicine_id": "MED-060", "name": "Albumin Human 20% 100ml", "category": "Critical Care", "unit_price": 3200.00, "is_critical": True, "storage_type": "Cold Chain 2-8C"}
]

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon coordinates."""
    import math
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def generate_synthetic_dataset():
    base_date = datetime(2026, 8, 14) # Reference date
    
    # 1. Write Pharmacies CSV
    pharmacy_path = os.path.join(DATA_DIR, "synthetic_pharmacies.csv")
    with open(pharmacy_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pharmacy_id", "pharmacy_name", "city", "latitude", "longitude", "storage_capacity", "operating_status"])
        writer.writeheader()
        for p in PHARMACIES:
            writer.writerow(p)
    print(f"[OK] Generated {len(PHARMACIES)} pharmacies -> {pharmacy_path}")

    # 2. Write Medicines CSV
    medicine_path = os.path.join(DATA_DIR, "synthetic_medicines.csv")
    with open(medicine_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["medicine_id", "name", "category", "unit_price", "is_critical", "storage_type"])
        writer.writeheader()
        for m in MEDICINES:
            writer.writerow(m)
    print(f"[OK] Generated {len(MEDICINES)} medicines -> {medicine_path}")

    # 3. Write Demand Forecast CSV
    demand_records = []
    demand_path = os.path.join(DATA_DIR, "synthetic_demand.csv")
    for p in PHARMACIES:
        for m in MEDICINES:
            # Baseline demand variation based on medicine category and pharmacy size
            if p["operating_status"] == "CLOSED":
                daily = 0.0
                weekly = 0.0
                monthly = 0.0
                hist = 0.0
                trend = "ZERO"
            elif m["is_critical"] or m["category"] in ["Antibiotic", "Cardiovascular", "Antidiabetic"]:
                daily = round(random.uniform(3.0, 25.0), 2)
                weekly = round(daily * 7 * random.uniform(0.9, 1.1), 2)
                monthly = round(daily * 30 * random.uniform(0.9, 1.1), 2)
                hist = round(monthly * random.uniform(0.8, 1.2), 2)
                trend = random.choice(["STABLE", "INCREASING", "INCREASING", "DECREASING"])
            else:
                daily = round(random.uniform(0.5, 12.0), 2)
                weekly = round(daily * 7 * random.uniform(0.85, 1.15), 2)
                monthly = round(daily * 30 * random.uniform(0.85, 1.15), 2)
                hist = round(monthly * random.uniform(0.7, 1.3), 2)
                trend = random.choice(["STABLE", "DECREASING", "INCREASING", "VOLATILE"])

            # Create specific demand asymmetries for testing redistribution
            if p["pharmacy_id"] in ["PHARM-001", "PHARM-005"] and m["medicine_id"] in ["MED-001", "MED-002", "MED-005", "MED-018", "MED-019", "MED-060"]:
                daily = round(random.uniform(0.5, 2.0), 2) # Excess source
                trend = "DECREASING"
            elif p["pharmacy_id"] in ["PHARM-002", "PHARM-003", "PHARM-007", "PHARM-011"] and m["medicine_id"] in ["MED-001", "MED-002", "MED-005", "MED-018", "MED-019", "MED-060"]:
                daily = round(random.uniform(15.0, 35.0), 2) # High demand destination
                trend = "INCREASING"

            demand_records.append({
                "medicine_id": m["medicine_id"],
                "pharmacy_id": p["pharmacy_id"],
                "daily_demand": daily,
                "weekly_demand": weekly,
                "monthly_demand": monthly,
                "historical_demand": hist,
                "demand_trend": trend
            })

    with open(demand_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["medicine_id", "pharmacy_id", "daily_demand", "weekly_demand", "monthly_demand", "historical_demand", "demand_trend"])
        writer.writeheader()
        for d in demand_records:
            writer.writerow(d)
    print(f"[OK] Generated {len(demand_records)} demand profiles -> {demand_path}")

    # 4. Generate 5,200+ Realistic Inventory Batches with all shelf-life categories & Edge Cases
    inventory_records = []
    inventory_path = os.path.join(DATA_DIR, "synthetic_inventory.csv")
    
    batch_counter = 1000

    # Distribute batches across pharmacies
    for p in PHARMACIES:
        p_id = p["pharmacy_id"]
        num_batches = random.randint(290, 320) if p["operating_status"] != "CLOSED" else 40
        
        for _ in range(num_batches):
            batch_counter += 1
            inv_id = f"INV-{batch_counter:06d}"
            med = random.choice(MEDICINES)
            med_id = med["medicine_id"]
            batch_code = f"BAT-{med_id.split('-')[1]}-{random.randint(100, 999)}"
            
            # Received date: 30 to 360 days ago
            days_ago = random.randint(30, 360)
            received_dt = base_date - timedelta(days=days_ago)
            
            # Distribution of remaining shelf life:
            # ~8% Expired (< 0 days)
            # ~12% Critical (1 - 7 days)
            # ~20% High Risk (8 - 30 days)
            # ~25% Medium Risk (31 - 60 days)
            # ~35% Healthy / Normal (> 60 days)
            r = random.random()
            if r < 0.08:
                expiry_dt = base_date - timedelta(days=random.randint(1, 45))
                stock_status = "EXPIRED"
            elif r < 0.20:
                expiry_dt = base_date + timedelta(days=random.randint(1, 7))
                stock_status = "NEAR_EXPIRY"
            elif r < 0.40:
                expiry_dt = base_date + timedelta(days=random.randint(8, 30))
                stock_status = "NEAR_EXPIRY"
            elif r < 0.65:
                expiry_dt = base_date + timedelta(days=random.randint(31, 60))
                stock_status = "AVAILABLE"
            else:
                expiry_dt = base_date + timedelta(days=random.randint(61, 400))
                stock_status = "AVAILABLE"

            # Quantities
            if stock_status == "NEAR_EXPIRY":
                quantity = random.choice([
                    random.randint(10, 40),
                    random.randint(50, 180),
                    random.randint(200, 450)
                ])
            else:
                quantity = random.randint(20, 250)

            inventory_records.append({
                "inventory_id": inv_id,
                "medicine_id": med_id,
                "medicine_name": med["name"],
                "medicine_category": med["category"],
                "batch_id": batch_code,
                "pharmacy_id": p_id,
                "quantity": quantity,
                "unit_price": med["unit_price"],
                "expiry_date": expiry_dt.strftime("%Y-%m-%d"),
                "received_date": received_dt.strftime("%Y-%m-%d"),
                "stock_status": stock_status,
                "edge_case_tag": "NONE"
            })

    # Instate 8 Explicit Edge Cases
    edge_cases = [
        # Edge Case 1: Stock expires before transfer can complete (DTE = 1 day, Transit = 3 days)
        {
            "inventory_id": "INV-EDGE-001",
            "medicine_id": "MED-019",
            "medicine_name": "Meropenem 1g Injection",
            "medicine_category": "Antibiotic",
            "batch_id": "BAT-EDGE-EXP-TRANSIT",
            "pharmacy_id": "PHARM-001",
            "quantity": 100,
            "unit_price": 850.00,
            "expiry_date": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "received_date": (base_date - timedelta(days=120)).strftime("%Y-%m-%d"),
            "stock_status": "NEAR_EXPIRY",
            "edge_case_tag": "EXPIRES_BEFORE_TRANSIT"
        },
        # Edge Case 2: No destination pharmacy has meaningful demand
        {
            "inventory_id": "INV-EDGE-002",
            "medicine_id": "MED-060",
            "medicine_name": "Albumin Human 20% 100ml",
            "medicine_category": "Critical Care",
            "batch_id": "BAT-EDGE-NO-DEMAND",
            "pharmacy_id": "PHARM-010",
            "quantity": 80,
            "unit_price": 3200.00,
            "expiry_date": (base_date + timedelta(days=20)).strftime("%Y-%m-%d"),
            "received_date": (base_date - timedelta(days=90)).strftime("%Y-%m-%d"),
            "stock_status": "NEAR_EXPIRY",
            "edge_case_tag": "NO_DESTINATION_DEMAND"
        },
        # Edge Case 3: Source quantity is below safety threshold
        {
            "inventory_id": "INV-EDGE-003",
            "medicine_id": "MED-004",
            "medicine_name": "Metformin 500mg SR",
            "medicine_category": "Antidiabetic",
            "batch_id": "BAT-EDGE-LOW-SOURCE",
            "pharmacy_id": "PHARM-002",
            "quantity": 6,
            "unit_price": 45.00,
            "expiry_date": (base_date + timedelta(days=15)).strftime("%Y-%m-%d"),
            "received_date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
            "stock_status": "NEAR_EXPIRY",
            "edge_case_tag": "BELOW_SAFETY_STOCK"
        },
        # Edge Case 4: Missing or invalid expiry date
        {
            "inventory_id": "INV-EDGE-004",
            "medicine_id": "MED-002",
            "medicine_name": "Amoxicillin + Clavulanate 625mg",
            "medicine_category": "Antibiotic",
            "batch_id": "BAT-EDGE-INVALID-DATE",
            "pharmacy_id": "PHARM-003",
            "quantity": 120,
            "unit_price": 185.00,
            "expiry_date": "INVALID_DATE",
            "received_date": (base_date - timedelta(days=40)).strftime("%Y-%m-%d"),
            "stock_status": "NEAR_EXPIRY",
            "edge_case_tag": "INVALID_EXPIRY_DATE"
        },
        # Edge Case 5: Destination pharmacy is closed
        {
            "inventory_id": "INV-EDGE-005",
            "medicine_id": "MED-007",
            "medicine_name": "Telmisartan 40mg",
            "medicine_category": "Cardiovascular",
            "batch_id": "BAT-EDGE-DEST-CLOSED",
            "pharmacy_id": "PHARM-004",
            "quantity": 150,
            "unit_price": 78.00,
            "expiry_date": (base_date + timedelta(days=22)).strftime("%Y-%m-%d"),
            "received_date": (base_date - timedelta(days=70)).strftime("%Y-%m-%d"),
            "stock_status": "NEAR_EXPIRY",
            "edge_case_tag": "DESTINATION_CLOSED_ONLY"
        },
        # Edge Case 6: Already expired medicine
        {
            "inventory_id": "INV-EDGE-006",
            "medicine_id": "MED-018",
            "medicine_name": "Enoxaparin 40mg Injection",
            "medicine_category": "Cardiovascular",
            "batch_id": "BAT-EDGE-ALREADY-EXPIRED",
            "pharmacy_id": "PHARM-005",
            "quantity": 75,
            "unit_price": 450.00,
            "expiry_date": (base_date - timedelta(days=15)).strftime("%Y-%m-%d"),
            "received_date": (base_date - timedelta(days=200)).strftime("%Y-%m-%d"),
            "stock_status": "EXPIRED",
            "edge_case_tag": "ALREADY_EXPIRED"
        },
        # Edge Case 7: Sudden demand collapse
        {
            "inventory_id": "INV-EDGE-007",
            "medicine_id": "MED-013",
            "medicine_name": "Montelukast + Levocetirizine",
            "medicine_category": "Respiratory",
            "batch_id": "BAT-EDGE-DEMAND-COLLAPSE",
            "pharmacy_id": "PHARM-006",
            "quantity": 300,
            "unit_price": 115.00,
            "expiry_date": (base_date + timedelta(days=25)).strftime("%Y-%m-%d"),
            "received_date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
            "stock_status": "NEAR_EXPIRY",
            "edge_case_tag": "SUDDEN_DEMAND_DROP"
        },
        # Edge Case 8: Duplicate batch across different locations
        {
            "inventory_id": "INV-EDGE-008A",
            "medicine_id": "MED-005",
            "medicine_name": "Human Regular Insulin 100IU",
            "medicine_category": "Antidiabetic",
            "batch_id": "BAT-DUPLICATE-999",
            "pharmacy_id": "PHARM-001",
            "quantity": 110,
            "unit_price": 350.00,
            "expiry_date": (base_date + timedelta(days=18)).strftime("%Y-%m-%d"),
            "received_date": (base_date - timedelta(days=50)).strftime("%Y-%m-%d"),
            "stock_status": "NEAR_EXPIRY",
            "edge_case_tag": "DUPLICATE_BATCH"
        },
        {
            "inventory_id": "INV-EDGE-008B",
            "medicine_id": "MED-005",
            "medicine_name": "Human Regular Insulin 100IU",
            "medicine_category": "Antidiabetic",
            "batch_id": "BAT-DUPLICATE-999",
            "pharmacy_id": "PHARM-008",
            "quantity": 40,
            "unit_price": 350.00,
            "expiry_date": (base_date + timedelta(days=18)).strftime("%Y-%m-%d"),
            "received_date": (base_date - timedelta(days=50)).strftime("%Y-%m-%d"),
            "stock_status": "NEAR_EXPIRY",
            "edge_case_tag": "DUPLICATE_BATCH"
        }
    ]
    inventory_records.extend(edge_cases)

    with open(inventory_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["inventory_id", "medicine_id", "medicine_name", "medicine_category", "batch_id", "pharmacy_id", "quantity", "unit_price", "expiry_date", "received_date", "stock_status", "edge_case_tag"])
        writer.writeheader()
        for inv in inventory_records:
            writer.writerow(inv)
    print(f"[OK] Generated {len(inventory_records)} inventory records -> {inventory_path}")

    # 5. Write Transfer Route Matrix
    transfers = []
    transfer_path = os.path.join(DATA_DIR, "synthetic_transfers.csv")
    for p1 in PHARMACIES:
        for p2 in PHARMACIES:
            if p1["pharmacy_id"] != p2["pharmacy_id"]:
                dist = calculate_haversine_distance(p1["latitude"], p1["longitude"], p2["latitude"], p2["longitude"])
                transit_days = 1 if dist < 15.0 else (2 if dist < 30.0 else 3)
                cost = round(50.0 + (dist * 4.5), 2)
                transfers.append({
                    "source_pharmacy_id": p1["pharmacy_id"],
                    "destination_pharmacy_id": p2["pharmacy_id"],
                    "distance_km": dist,
                    "estimated_transfer_days": transit_days,
                    "transfer_cost": cost
                })

    with open(transfer_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source_pharmacy_id", "destination_pharmacy_id", "distance_km", "estimated_transfer_days", "transfer_cost"])
        writer.writeheader()
        for t in transfers:
            writer.writerow(t)
    print(f"[OK] Generated {len(transfers)} inter-pharmacy transfer routes -> {transfer_path}")

if __name__ == "__main__":
    generate_synthetic_dataset()
