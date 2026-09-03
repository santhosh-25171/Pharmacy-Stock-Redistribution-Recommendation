# Failure Modes, Operational Edge Cases & Mitigation Strategies

This document catalogs real-world failure scenarios in pharmacy inventory redistribution, their potential root causes, operational risks, and the automated mitigation guards built into this platform.

---

## Systematic Edge-Case Analysis Matrix

| # | Edge Case Scenario | Root Cause | Potential Failure Impact | Automated Mitigation / System Guard |
|---|---|---|---|---|
| **1** | **Stock Expires Before Transit Completes** | Long inter-branch distance or unexpected courier delay exceeding remaining shelf-life. | Medicine arrives expired at destination; courier costs wasted; compliance violation. | **RULE-01 Guard**: Minimum 3 days remaining shelf-life required *after* transit duration is subtracted. |
| **2** | **No Meaningful Destination Demand** | Rare or specialized medication with low network-wide dispensing. | Relocating dead stock to another shelf without consumption benefit. | **RULE-02 Guard**: Minimum destination daily demand threshold ($\ge 0.8$ units/day) enforced. |
| **3** | **Insufficient Source Excess Stock** | All local stock is needed to fulfill imminent local prescriptions. | Creates artificial stockout and patient denial at the source pharmacy. | **RULE-03 Guard**: 3-day local safety stock buffer strictly deducted before calculating transferable excess. |
| **4** | **Missing or Invalid Expiry Date Format** | Data entry typo, corrupted barcode scan, or legacy ERP field corruption. | Unpredictable automated decision on potentially dangerous medication. | **RULE-04 Guard**: String date sanitizer quarantines malformed records (`INVALID_DATE`) and blocks automated routing. |
| **5** | **Destination Pharmacy Closed / Maintenance** | Temporary store renovation, power failure, or regulatory suspension. | Shipment arrives at locked facility; risk of cold-chain break. | **RULE-05 Guard**: Real-time operating status filter (`ACTIVE` branches only). |
| **6** | **Already Expired Medication** | Overlooked batch sitting in physical stockroom. | Unlawful transfer of non-dispensable pharmaceutical waste. | **RULE-06 Guard**: Hard clinical block for $DTE \le 0$ days. Disables transfer and triggers disposal workflow. |
| **7** | **Sudden Local Demand Collapse** | Physician prescription habit changes or seasonal drop. | Previously adequate stock suddenly becomes high-risk excess. | **RULE-07 Guard**: Dynamic 7-day rolling velocity recalculation immediately flags new excess for redistribution. |
| **8** | **Duplicate Batch Codes Across Branches** | Central distributor splits same manufacturing lot across multiple branches. | Race conditions or database collisions during transfer logging. | **RULE-08 Guard**: Primary key tracking at granular `Inventory_ID` level prevents multi-branch batch collisions. |

---

## Human Decision Override & Rejection Handling
To ensure operational realism and prevent friction:
1. Pharmacists can reject recommendations by selecting structured reasons (e.g., *Physical stock count differs*, *Destination already received stock*, *Medicine quality concern*).
2. Pharmacists can override the recommended quantity if physical shelf storage or transport capacity differs from ERP database records.
3. Every human interaction updates network metrics and logs an immutable audit event for supply chain review.
