# Operational Workflow & System Architecture

```mermaid
flowchart TD
    A[Synthetic Inventory Batch & Demand Data] --> B[Expiry Risk Scorer]
    B --> C{Days to Expiry <= 30d?}
    C -- No --> D[Normal Stock: Local Dispensing]
    C -- Yes --> E[Calculate Local Excess & Safety Stock Buffer]
    E --> F{Excess > 5 Units?}
    F -- No --> G[Expedite Local First-In First-Out Dispensing]
    F -- Yes --> H[Candidate Destination Discovery & Ranking Engine]
    H --> I[Filter Active Branches & Validate Storage Capacity]
    I --> J[Calculate Haversine Distance & Transit Days]
    J --> K{Remaining Shelf Life Post-Transit >= 3 Days?}
    K -- No --> L[Block Transfer: Risk of In-Transit Expiration]
    K -- Yes --> M[Calculate Optimal Transfer Qty & Explainable Evidence]
    M --> N[Flag High-Impact Actions Value > ₹2000 or Urgent DTE]
    N --> O[Generate Recommendation in Database]
    O --> P[Human Pharmacist / Manager Review Interface]
    P --> Q{Human Action}
    Q -- Approve --> R[Log Transfer Action & Dispatch Notification]
    Q -- Reject --> S[Capture Mandatory Rejection Reason & Audit Log]
    Q -- Override --> T[Update Quantity, Recalculate Savings & Audit Log]
    R --> U[Update Protected Stock Value in Real-time Analytics]
```

## Step-by-Step Operational Workflow

### 1. Ingestion & Continuous Risk Auditing
- The system continuously parses inventory batch records from the PostgreSQL database.
- Batches are classified into **CRITICAL** ($\le 7$ days), **HIGH** (8–30 days), **MEDIUM** (31–60 days), **LOW** ($>60$ days), or **EXPIRED** ($\le 0$ days).

### 2. Local Excess & Safety Buffer Calculation
- Using either rolling historical velocity or ML-predicted daily demand, the engine calculates how many units can realistically be dispensed locally before expiration.
- A 3-day local safety stock buffer is reserved to protect against immediate patient walk-in shortages at the source branch.

### 3. Destination Candidate Discovery & Ranking
- For batches with surplus stock, the engine evaluates all active candidate pharmacies in the metropolitan network.
- The ranking objective function balances:
  $$\text{Score} = (\text{Destination Demand Velocity} \times 12.0) + (\text{Post-Transit Shelf Life} \times 2.5) - (\text{Distance km} \times 0.35)$$
- Life-saving / critical medications receive priority weighting.

### 4. Explainable Evidence & Impact Evaluation
- Recommendations are accompanied by factual evidence bullets detailing transit distance, velocity comparison, capacity window, and protected monetary value.
- Transfers exceeding ₹2,000 or involving $< 14$ days shelf-life are flagged as **High-Impact**, requiring explicit confirmation.

### 5. Human-in-the-Loop Oversight & Immutable Audit Trail
- Branch pharmacists and regional supply chain managers review recommendations in the web dashboard.
- Every approval, rejection reason, or quantity override is cryptographically linked to the user's role and permanently recorded in the immutable audit log table.
