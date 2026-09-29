"""
Authentication, Direct Bcrypt Password Hashing and JWT Helpers with Role-Based Access Control (RBAC).
Provides cryptographically secure credentials verification and scoped route authorization.
"""

import os
import logging
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.app.database.session import get_db

logger = logging.getLogger("pharmacy.security")

# Secret key resolution: In production, this must be set via the SECRET_KEY environment variable.
# In local dev/evaluation, fallback to a standard development key.
DEFAULT_DEV_SECRET = "pharmacy_redistribution_secret_key_2026_antigravity"
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_DEV_SECRET)
if SECRET_KEY == DEFAULT_DEV_SECRET and os.getenv("ENVIRONMENT") == "production":
    logger.warning("[SECURITY WARNING] Running with default development SECRET_KEY in production! Set SECRET_KEY in .env.")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24))) # 24 hours

# OAuth2 bearer token scheme reading Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a stored bcrypt hash.
    
    Why: Bcrypt natively truncates passwords at 72 bytes. Explicitly slicing to 72 bytes
    prevents denial-of-service edge cases while preserving cryptographic salt verification.
    """
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Generates a secure salted bcrypt hash (rounds=10).
    
    Why: Cost factor 10 provides optimal balance between resistance to brute-force
    GPU attacks and snappy login latency on standard server hardware (~80ms).
    """
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encodes claims into a signed HS256 JWT access token.
    
    Why: Timezone-aware UTC timestamps ensure deterministic token expiration
    across distributed server deployments without local timezone drift.
    """
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency that decodes the Bearer JWT, validates signature, and fetches active user from database.
    
    Why: Validating user status in the database on each request ensures revoked or inactive
    users are immediately denied access even if their token has not reached its TTL.
    """
    from backend.app.models import User
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def require_roles(allowed_roles: List[str]):
    """
    Enforces Role-Based Access Control (RBAC) on FastAPI endpoints.
    
    Why: Defense in depth requires backend endpoint authorization rather than relying
    solely on frontend UI hiding. Normal pharmacists cannot call admin endpoints (e.g. database reseed)
    or view network-wide audit logs.
    """
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User role '{current_user.role}' lacks permission for this action. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker
