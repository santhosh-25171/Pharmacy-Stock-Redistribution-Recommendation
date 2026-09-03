# Prototype Stakeholder Walkthrough & Validation

*Note: The following represents a structured prototype walkthrough with simulated user personas to validate workflow completeness and usability.*

## Persona 1: Senior Retail Pharmacist (Central Hub - PHARM-001)
- **Primary Goal**: Quickly identify near-expiry excess in the store and approve safe outgoing transfers without starving local walk-in customers.
- **Walkthrough Evaluation**:
  - *Task 1: Locate batches expiring within 30 days* &rarr; Found in 1 click via Inventory Risk Filter (`CRITICAL` / `HIGH`).
  - *Task 2: Understand why transfer was recommended* &rarr; Opened "Why Recommended?" modal; verified that local daily velocity is 1.5 units/day while destination dispenses 18.0 units/day.
  - *Task 3: Authorize high-impact shipment* &rarr; Reviewed value (₹4,200), checked mandatory confirmation checkbox, and approved. Audit log recorded action.
- **Observed Feedback**: Requested clear indication of remaining shelf-life after courier transit. Implemented in Evidence Modal.

---

## Persona 2: Regional Supply Chain Manager
- **Primary Goal**: Track total capital saved across the 18-pharmacy network and evaluate redistribution efficiency against standard FIFO.
- **Walkthrough Evaluation**:
  - *Task 1: Review aggregate network KPIs* &rarr; Inspected Total Inventory Value (₹2.4 Cr), Near-Expiry Value (₹18.5 Lakhs), and Value Protected (₹83.1 Lakhs).
  - *Task 2: Benchmark against naive FIFO baseline* &rarr; Inspected Analytics page; verified +₹7.44 Lakhs (+9.88%) average monetary improvement.
  - *Task 3: Configure escalation rules* &rarr; Navigated to Settings; adjusted High-Value cutoff to ₹2,000.
- **Observed Feedback**: Requested the ability to filter audit history by specific rejection reasons. Implemented in Audit Log filters.

---

## Persona 3: Inventory Coordinator & Compliance Auditor
- **Primary Goal**: Verify that expired or hazardous medication batches cannot be transferred across branch locations.
- **Walkthrough Evaluation**:
  - *Task 1: Test edge cases (expired batch, transit > shelf-life, closed store)* &rarr; Navigated to Edge Cases Sandbox; verified all 8 edge cases were automatically blocked with exact rule codes.
  - *Task 2: Audit human decision compliance* &rarr; Inspected Audit Trail; verified every override recorded the actor's email, role, old quantity, and override justification.
- **Observed Feedback**: Emphasized the importance of a visible synthetic data disclosure. Implemented in Navbar banner and Privacy Center.
