# Authentication, RBAC, and Protected Routing Architecture

This document details the security, authentication, and role-based authorization architecture in PharmaShift.

---

## 1. Login-First Security Flow

In Review #3, PharmaShift enforces a strict **Login-First** user experience. Direct access to operational dashboards without a verified cryptographic session is physically impossible.

```
       User Opens Application (http://localhost:3000)
                             │
                             ▼
               Is JWT Token in localStorage?
                    ├── No ───► Render <Login /> Page
                    └── Yes ──► Send GET /api/auth/me
                                  ├── 200 OK ──► Render Protected Dashboard
                                  └── 401/Err ─► Clear Token ──► Render <Login />
```

### Key Principles:
1. **No Default Bypass**: The application never automatically logs into an administrative session unless explicitly authorized by the user.
2. **Deterministic Redirect**: Any route or state alteration while unauthenticated immediately presents the Login interface.
3. **Session Invalidation**: When a token expires or is rejected by backend APIs with HTTP 401, the client-side session is cleared immediately, redirecting the user to the Login screen with an alert banner.

---

## 2. JWT Implementation & Token Lifecycle

- **Algorithm**: `HS256` (HMAC with SHA-256)
- **Token Type**: Bearer Access Token
- **Default TTL**: 1,440 minutes (24 hours), configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Secret Key**: Configured via `SECRET_KEY` environment variable. Falls back to a deterministic development key with loud console security warnings if running in production.

### Token Claims Structure:
```json
{
  "sub": "admin@pharmacy.io",
  "role": "ADMIN",
  "assigned_pharmacy_id": null,
  "exp": 1726056000
}
```

- **`sub`**: Subject user email used to look up and re-validate active account status in the database on every authenticated request.
- **`role`**: User privilege level used for fast frontend navigation scoping and backend authorization checks.
- **`assigned_pharmacy_id`**: Associated branch identifier (e.g. `'PHARM-001'`). If null, the user possesses network-wide administrative oversight.
- **`exp`**: UTC expiration epoch timestamp enforcing session bounds.

---

## 3. Password Hashing & Bcrypt Security

PharmaShift uses standard salted bcrypt hashing via the Python `bcrypt` library (`backend/app/utils/security.py`):
- **Salt Rounds**: 10 rounds (~80ms derivation time per verification).
- **72-Byte Truncation Safety**: Passwords are explicitly encoded and sliced to `[:72]` bytes before passing to bcrypt, preventing buffer boundary overflow issues and algorithmic denial-of-service.
- **Zero Plaintext Persistence**: Plaintext passwords are never written to disk, database columns, terminal logs, or audit records.

---

## 4. Role-Based Access Control (RBAC) Matrix

PharmaShift implements three distinct operational roles across the network:

| Role | Administrative Functions | Network Overview | Batch Redistribution | Branch Scoping | Audit Logs |
|---|:---:|:---:|:---:|:---:|:---:|
| **`ADMIN`** | Full (`/api/seed`, reset) | Full (All 18 branches) | Full (Approve / Reject / Override) | Network-Wide | Full Read Access |
| **`MANAGER`** | Restricted (No seed/reset) | Full (All 18 branches) | Full (Approve / Reject / Override) | Network-Wide | Full Read Access |
| **`PHARMACIST`** | None | Scoped | Scoped (Only outgoing from branch) | Scoped (e.g. `PHARM-001`) | Denied (HTTP 403) |

### Backend RBAC Enforcement:
Backend routes use the `require_roles(...)` dependency:
```python
@router.post("/api/seed", tags=["Admin"])
def force_reseed(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    ...
```

If an unauthorized role attempts to invoke the endpoint, FastAPI halts execution immediately and returns **`HTTP 403 Forbidden`**.

---

## 5. Client-Side Protected Routing & Error Boundaries

- **State Container**: `frontend/src/context/AuthContext.jsx` manages `user`, `token`, `loading`, and `error`.
- **Protected Layout**: In `frontend/src/App.jsx`:
  ```jsx
  if (loading) return <LoadingScreen />;
  if (!user) return <Login />;
  return <ProtectedAppLayout />;
  ```
- **Error Boundaries**: Every individual page view within `<ProtectedAppLayout />` is wrapped in `<ErrorBoundary sectionName="...">` to guarantee that unexpected UI rendering failures never terminate the authenticated session.

---

## 6. Logout Protocol

Users can securely terminate their session via:
1. **Navbar Direct Logout Button**: Located on the top navigation bar.
2. **User Profile Dropdown**: Contains a dedicated "Sign Out" item.
3. **Sidebar Logout Action**: Positioned at the base of the navigation sidebar.

### Execution Steps:
1. `localStorage.removeItem('pharmacy_token')` deletes the client-side credential.
2. Internal React state (`token`, `user`) is reset to `null`.
3. The UI immediately unmounts all protected application views and renders `<Login />`.
4. Subsequent API calls fail with `HTTP 401`, preventing cached request replay.

---

## 7. Review Evaluation Demo Accounts

For evaluation and demonstration purposes, standard development accounts are pre-seeded into the SQLite/PostgreSQL databases:

| Role | Email | Password | Assigned Scope | Description |
|---|---|---|---|---|
| **ADMIN** | `admin@pharmacy.io` | `Admin@123` | Network-Wide | System Administrator with full access to re-seed, audit logs, and network transfers |
| **MANAGER** | `manager@pharmacy.io` | `Manager@123` | Network-Wide | Regional Supply Chain Manager overseeing inventory, approvals, and simulation benchmarks |
| **PHARMACIST** | `pharmacist@pharmacy.io` | `Pharmacist@123` | `PHARM-001` | Senior Pharmacist scoped to Central Hub Pharmacy |
| **PHARMACIST 2**| `pharmacist2@pharmacy.io`| `Pharmacist@123` | `PHARM-002` | Duty Pharmacist scoped to Indiranagar Branch |

> [!TIP]
> The **Login Page** features a convenient **Review Evaluation Quick-Fill** panel allowing reviewers to click any of the 4 demo accounts to instantly populate credentials.
