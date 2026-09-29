# Error Handling & Resilience Architecture

This document details the dual-layer resilience architecture implemented in PharmaShift:
1. **Frontend**: React Error Boundaries and stateful recovery controls.
2. **Backend**: HTTP exception standardization, input validation sanitization, and unhandled exception isolation.

---

## 1. Frontend Error Boundaries

### 1.1 What is an Error Boundary?
In React, an unhandled JavaScript error inside a component lifecycle method or render function unmounts the entire application tree, resulting in a blank white screen. 

A **React Error Boundary** is a higher-order class component that catches JavaScript errors anywhere in its child component tree, logs the error, and renders a fallback UI instead of crashing the entire interface.

### 1.2 Implementation in PharmaShift
The `ErrorBoundary` component is implemented in `frontend/src/components/ErrorBoundary.jsx`:
- **`getDerivedStateFromError(error)`**: Updates boundary state to render fallback UI on the next render cycle.
- **`componentDidCatch(error, errorInfo)`**: Logs diagnostic metadata to the console for developer debugging without leaking internal execution details to end users.
- **`handleRetry()`**: Resets boundary state (`hasError: false`), allowing the user to recover the view without losing their authenticated session.

### 1.3 Where Error Boundaries are Placed
Error boundaries are strategically wrapped around every major dashboard section in `frontend/src/App.jsx`:
- **Dashboard**: Isolates KPI computation and chart rendering errors.
- **Inventory Monitor**: Isolates large-table data processing and filter errors.
- **Transfer Recommendations**: Isolates recommendation list and action modal errors.
- **Pharmacy Network**: Isolates map coordinate rendering and branch detail cards.
- **Analytics & Simulation Benchmarks**: Isolates Recharts SVG calculations.
- **Edge Cases Sandbox**: Isolates synthetic failure rule demonstrations.
- **Audit Trail**: Isolates historical log rendering.
- **Privacy & Settings**: Isolates administrative configuration panels.

### 1.4 What Error Boundaries Catch vs. Do NOT Catch

| Catches | Does NOT Catch |
|---|---|
| Errors during component rendering | Event handlers (e.g. `onClick`) — handled via `try/catch` |
| Errors in lifecycle methods (`componentDidMount`, etc.) | Asynchronous code (e.g. `setTimeout`, `requestAnimationFrame`) |
| Errors in constructors of whole tree below them | Server-side rendering (SSR) errors |
| Errors in child functional hooks | Errors thrown in the boundary itself (rather than children) |

### 1.5 User Experience & Recovery
When a rendering failure occurs:
1. The user sees a styled error card: *"Something went wrong while loading [Section Name]"*.
2. A brief, non-technical explanation informs the user that the section was isolated to protect active data.
3. The user has two recovery options:
   - **Retry Section**: Clears the boundary error state and re-executes the section render.
   - **Reload Application**: Hard-refreshes the browser while preserving authentication if the JWT remains valid.
4. Raw JavaScript stack traces, internal variable states, and file paths are **never displayed** to the user.

---

## 2. Backend Exception Handling

### 2.1 HTTP Status Code Conventions
FastAPI endpoints in PharmaShift adhere strictly to RESTful HTTP error semantics:

| HTTP Status | Semantic Meaning | Scenario in PharmaShift |
|---|---|---|
| **`400 Bad Request`** | Client sent invalid parameters or violated state machine logic | Attempting to approve an already approved recommendation; negative override quantity; missing rejection category; high-impact transfer without required confirmation checkbox |
| **`401 Unauthorized`** | Authentication credentials missing or invalid | Expired JWT token; missing `Authorization: Bearer` header; incorrect email/password on login |
| **`403 Forbidden`** | Authenticated user lacks permission for the resource | Pharmacist attempting to approve transfers outside their assigned pharmacy; non-admin attempting to invoke `/api/seed`; pharmacist attempting to access network `/api/audit-logs` |
| **`404 Not Found`** | Requested entity does not exist | Lookup for non-existent recommendation ID, batch ID, or pharmacy ID |
| **`422 Unprocessable Entity`** | Pydantic schema validation failure | Malformed JSON body; invalid data types (e.g. string passed where integer expected) |
| **`500 Internal Server Error`** | Unexpected server-side failure | Database connection disruption; filesystem I/O fault |

### 2.2 Centralized Exception Handlers (`backend/app/main.py`)

#### 1. Starlette / FastAPI `HTTPException` Handler
Ensures consistent JSON error format while preserving HTTP status headers and custom error messages:
```json
{
  "detail": "High-impact transfer requires explicit human confirmation checkbox.",
  "error_type": "HTTPException",
  "status_code": 400
}
```

#### 2. Pydantic `RequestValidationError` (422)
Sanitizes raw Pydantic validation exceptions, formatting field-level errors clearly:
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "overridden_quantity"],
      "msg": "Input should be a valid integer"
    }
  ],
  "error_type": "ValidationError",
  "status_code": 422
}
```

#### 3. Unhandled Global Exception Handler (500)
Catches any uncaught Python exceptions (`Exception`), records full traceback to server logs (`logger.error`), and returns a safe response without exposing stack traces or database schema details:
```json
{
  "detail": "An internal server error occurred. Please contact the system administrator.",
  "error_type": "InternalServerError",
  "status_code": 500
}
```

---

## 3. Client-Side API Failure Interception

In `frontend/src/services/api.js`:
- An Axios response interceptor monitors all outgoing HTTP calls.
- When an API call returns **`401 Unauthorized`** (e.g. token expired after 24 hours):
  1. The invalid token is removed from `localStorage`.
  2. A global `auth:unauthorized` event is broadcast.
  3. `AuthContext` catches the event, resets user state to `null`, and instantly transitions the user back to the **Login Page** with a session expiration notice.
  4. The user cannot remain on or navigate through protected dashboard pages with a dead token.
