# Problem Analysis: Expiry-Aware Pharmacy Stock Redistribution

## 1. Executive Summary & Problem Context
In multi-branch retail and hospital pharmacy chains, medication expiry represents one of the largest drivers of operational waste, capital loss, and pharmaceutical destruction. Millions of dollars worth of vital medications reach their expiration date in low-turnover suburban or satellite clinics while central hospital hubs or high-density retail locations experience stock shortages for those exact same formulations.

### Core Challenges Identified:
1. **Isolated Inventory Silos**: Individual pharmacy branches operate on localized ordering patterns without visibility into real-time cross-branch expiration horizons.
2. **Lagging Expiry Discovery**: Near-expiry batches ($< 30$ days) are frequently identified only during manual monthly physical audits—too late to legally redistribute or dispense before expiration.
3. **Complex Logistics Constraints**: Blind redistribution often fails because transit duration, temperature requirements, destination demand velocity, and available destination shelf capacity are not mathematically reconciled against remaining batch shelf-life.
4. **Lack of Trust / Black-Box Models**: Pharmacists and inventory managers are reluctant to act on automated relocation recommendations unless the underlying evidence and financial impact are 100% transparent, explainable, and verifiable.

---

## 2. Mathematical Formulation & Redistribution Constraints

Let:
- $B_i$ be an inventory batch of medicine $m$ located at source pharmacy $P_{\text{src}}$ with remaining shelf-life $DTE(B_i)$ (Days to Expiry) and quantity $Q_i$.
- $D(P_k, m)$ be the daily dispensing demand rate of medicine $m$ at pharmacy $P_k$.
- $T_{\text{transit}}(P_{\text{src}}, P_{\text{dest}})$ be the estimated logistics transit time in days between $P_{\text{src}}$ and candidate destination $P_{\text{dest}}$.
- $S(P_{\text{src}}, m) = 3 \times D(P_{\text{src}}, m)$ be the mandatory local safety stock reservation at the source branch.
- $C(P_{\text{dest}})$ be the available storage capacity at the destination branch.

### Excess Stock at Source:
$$\text{Excess}(P_{\text{src}}, B_i) = \max\left(0, Q_i - \left[D(P_{\text{src}}, m) \times DTE(B_i)\right] - S(P_{\text{src}}, m)\right)$$

### Post-Transit Consumable Window at Destination:
$$\text{Consumable Window}(P_{\text{dest}}, B_i) = \max\left(0, DTE(B_i) - T_{\text{transit}}(P_{\text{src}}, P_{\text{dest}})\right) \times D(P_{\text{dest}}, m)$$

### Optimal Feasible Transfer Quantity:
$$Q^* = \min\left(\text{Excess}(P_{\text{src}}, B_i), \text{Consumable Window}(P_{\text{dest}}, B_i), C(P_{\text{dest}})\right)$$

### Recommendation Feasibility Guard:
A transfer recommendation is valid **if and only if**:
1. $DTE(B_i) - T_{\text{transit}}(P_{\text{src}}, P_{\text{dest}}) \ge 3 \text{ days}$ (Safety shelf-life buffer)
2. $\text{Status}(P_{\text{src}}) = \text{'ACTIVE'} \land \text{Status}(P_{\text{dest}}) = \text{'ACTIVE'}$
3. $Q^* \ge 5 \text{ units}$ (Minimum economic transfer threshold)
4. $D(P_{\text{dest}}, m) \ge 0.8 \text{ units/day}$ (Avoid dead-stock relocation)
5. $B_i \text{ is not expired or quarantined}$

---

## 3. Synthetic Operational Dataset Scope
To ensure strict privacy compliance, the prototype uses **100% synthetic operational pharmacy data**:
- **18 Synthetic Pharmacy Locations** across metropolitan zones with realistic latitude/longitude, capacity, and operating statuses.
- **60 Synthetic Medicines** spanning Antibiotics, Cardiovascular, Antidiabetic, Critical Care, Respiratory, and Analgesics.
- **5,000+ Inventory Batches** representing all lifecycle states (Expired, Critical $\le 7$d, High Risk 8–30d, Medium Risk 31–60d, Normal $>60$d).
- **8 Dedicated Edge-Case Batches** to validate system safety guards under operational failure modes.
- **Zero Real Patient Data (No PII)**: No patient names, phone numbers, addresses, or prescription records.
