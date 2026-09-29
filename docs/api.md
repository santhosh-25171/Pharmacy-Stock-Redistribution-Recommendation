# PharmaShift: Comprehensive REST API Reference Documentation

**Base URL**: `http://localhost:8000`  
**Interactive API Documentation**: `/docs` (Swagger UI) & `/redoc` (ReDoc)  
**Security Scheme**: HTTP Bearer JWT (`Authorization: Bearer <token>`)

---

## 1. Master API Endpoints Directory

| HTTP Method | Endpoint | Description | Auth Required | Role Required | Common Status Codes |
|---|---|---|:---:|:---:|---|
| **`GET`** | `/health` | Subsystem health telemetry (API, DB, ML, Recommender) | No | None | `200`, `500` |
| **`POST`** | `/api/seed` | Force database reseed with 5,000+ synthetic batches | Yes | `ADMIN` | `200`, `401`, `403` |
| **`POST`** | `/api/auth/login` | Authenticate credentials and receive Bearer JWT | No | None | `200`, `400`, `401`, `422` |
| **`GET`** | `/api/auth/me` | Fetch active user profile from Bearer token | Yes | Any | `200`, `401` |
| **`GET`** | `/api/inventory` | Search & filter network inventory batches (scoped) | Yes | Any (Scoped) | `200`, `401` |
| **`GET`** | `/api/inventory/{id}` | Inspect single inventory batch risk & excess metrics | Yes | Any (Scoped) | `200`, `401`, `403`, `404` |
| **`GET`** | `/api/pharmacies` | List all network pharmacy branches & coordinates | No | None | `200` |
| **`GET`** | `/api/pharmacies/{id}` | Detailed branch metrics, capacity, and stock risk | No | None | `200`, `404` |
| **`GET`** | `/api/medicines` | Query pharmaceutical master catalog & categories | No | None | `200` |
| **`GET`** | `/api/recommendations` | Browse transfer recommendations & evidence bullets | Yes | Any (Scoped) | `200`, `401` |
| **`GET`** | `/api/recommendations/{id}` | Single transfer recommendation detail & evidence | Yes | Any (Scoped) | `200`, `401`, `403`, `404` |
| **`POST`** | `/api/recommendations/{id}/approve` | Approve transfer (validates high-impact confirmation) | Yes | Any (Scoped) | `200`, `400`, `401`, `403`, `404` |
| **`POST`** | `/api/recommendations/{id}/reject` | Reject transfer with mandatory structured reason | Yes | Any | `200`, `400`, `401`, `404` |
| **`POST`** | `/api/recommendations/{id}/override` | Override transfer quantity with reason & value update | Yes | Any | `200`, `400`, `401`, `404` |
| **`POST`** | `/api/recommendations/generate` | Trigger live re-evaluation of recommendations | Yes | `ADMIN`, `MANAGER` | `200`, `401`, `403` |
| **`GET`** | `/api/analytics` | Aggregated network KPIs, risk distribution & savings | No | None | `200` |
| **`GET`** | `/api/evaluation` | 30-scenario simulation benchmarks vs. naive FIFO | No | None | `200` |
| **`POST`** | `/api/evaluation/run` | Execute live 30-scenario simulation suite | Yes | `ADMIN`, `MANAGER` | `200`, `401`, `403` |
| **`GET`** | `/api/audit-logs` | Immutable audit trail with filtering by action/user | Yes | `ADMIN`, `MANAGER` | `200`, `401`, `403` |
| **`GET`** | `/api/edge-cases` | Status and safety verification of all 8 edge cases | No | None | `200` |

---

## 2. Detailed Router Specifications

### 2.1 Health & Administration

#### `GET /health`
Returns live operational telemetry across subsystems.
- **Request Parameters**: None
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "pharmacy-redistribution-recommender",
  "database": "connected",
  "api": "healthy",
  "ml_model": {
    "status": "HEALTHY",
    "model_loaded": true,
    "model_name": "RandomForestRegressor",
    "n_estimators": 100,
    "mae": 1.2152,
    "rmse": 3.5170,
    "r2_score": 0.7523,
    "trained_at": "2026-08-14T10:00:00Z"
  },
  "recommender": {
    "status": "active",
    "active_recommendations": 18,
    "engine": "feasibility_constrained_velocity_ranking"
  },
  "reference_date": {
    "reference_date": "2026-08-14",
    "mode": "FIXED_DEMO",
    "description": "Deterministic synthetic benchmark reference date"
  },
  "timestamp": "2026-09-29T08:15:00Z"
}
```

#### `POST /api/seed`
Forces synthetic dataset re-population and initial recommendation generation.
- **Headers**: `Authorization: Bearer <ADMIN_JWT>`
- **Response `200 OK`**:
```json
{
  "status": "success",
  "message": "Database successfully re-seeded with 5,000+ batches by Administrator.",
  "admin_user": "admin@pharmacy.io"
}
```

---

### 2.2 Authentication Router (`/api/auth`)

#### `POST /api/auth/login`
Validates user credentials and issues a signed JWT token.
- **Request Body**:
```json
{
  "email": "admin@pharmacy.io",
  "password": "Admin@123"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@pharmacy.io",
    "full_name": "System Administrator",
    "role": "ADMIN",
    "assigned_pharmacy_id": null,
    "is_active": true
  }
}
```
- **Error Responses**:
  - `401 Unauthorized`: `"Incorrect email or password"`
  - `400 Bad Request`: `"Inactive user account"`

#### `GET /api/auth/me`
Retrieves current authenticated profile.
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Response `200 OK`**: Returns current `UserOut` schema.

---

### 2.3 Inventory Router (`/api/inventory`)

#### `GET /api/inventory`
Retrieves inventory batches with risk analysis. If the user has `role == "PHARMACIST"`, results are strictly scoped to `assigned_pharmacy_id`.
- **Query Parameters**:
  - `pharmacy_id` (string, optional)
  - `category` (string, optional)
  - `risk_level` (string, optional: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `EXPIRED`)
  - `search` (string, optional: matches drug name or batch ID)
  - `limit` (int, default: 200, max: 1000)
  - `offset` (int, default: 0)
- **Response `200 OK`**: Array of `InventoryBatchOut` objects.

#### `GET /api/inventory/{inventory_id}`
Returns granular excess stock and risk metrics for a single batch.
- **Errors**: `404 Not Found` if batch does not exist; `403 Forbidden` if pharmacist attempts cross-branch inspection.

---

### 2.4 Recommendations Router (`/api/recommendations`)

#### `GET /api/recommendations`
Returns generated transfer recommendations sorted by potential value saved descending.
- **Query Parameters**: `status` (`PENDING`, `APPROVED`, `REJECTED`, `OVERRIDDEN`), `risk_level`, `is_high_impact`.
- **Response `200 OK`**: Array of `RecommendationOut` objects with embedded `RecommendationEvidence` list.

#### `POST /api/recommendations/{rec_id}/approve`
Executes human-in-the-loop transfer approval.
- **Request Body**:
```json
{
  "notes": "Approved by senior pharmacist for afternoon logistics courier.",
  "confirmed_high_impact": true
}
```
- **Validation**: If `is_high_impact == true` and `confirmed_high_impact == false`, returns **`HTTP 400 Bad Request`** (*"High-impact transfer requires explicit human confirmation checkbox."*).

#### `POST /api/recommendations/{rec_id}/reject`
Rejects recommendation with mandatory structured reasoning.
- **Request Body**:
```json
{
  "reason_category": "Physical stock count differs",
  "custom_reason": "Shelf inspection shows only 15 units physically present."
}
```
- **Validation**: If `reason_category` is empty, returns **`HTTP 400 Bad Request`**.

#### `POST /api/recommendations/{rec_id}/override`
Overrides the transfer quantity and automatically recalculates protected value.
- **Request Body**:
```json
{
  "reason_category": "Manager decision",
  "custom_reason": "Reduced quantity to keep extra local safety buffer.",
  "overridden_quantity": 25
}
```
- **Validation**: If `overridden_quantity <= 0`, returns **`HTTP 400 Bad Request`**.

---

### 2.5 Analytics & Baseline Evaluation

#### `GET /api/analytics`
Calculates aggregated network metrics across inventory batches and recommendation decisions.
- **Response `200 OK`**: Returns total inventory value, near-expiry stock value, high-risk batch count, potential value saved, and acceptance rate.

#### `GET /api/evaluation`
Exposes the 30-scenario simulation benchmark comparing proposed system vs. isolated FIFO baseline.
- **Response `200 OK`**: Returns summary metrics (+₹7.44L value protected, -52.1% waste reduction) and detailed per-scenario metrics.

---

### 2.6 Audit Logs Router (`/api/audit-logs`)

#### `GET /api/audit-logs`
Provides immutable compliance history. Accessible only to `ADMIN` and `MANAGER` roles.
- **Query Parameters**: `action` (`APPROVED`, `REJECTED`, `OVERRIDDEN`, `SEEDED`), `user_email`, `limit` (default: 100).
- **Authorization**: Pharmacists receive **`HTTP 403 Forbidden`**.
