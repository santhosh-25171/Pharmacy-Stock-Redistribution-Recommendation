"""
Audit Logs Router.
Provides immutable historical trail for Admin and Manager roles.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import AuditLog, User
from backend.app.schemas import AuditLogOut
from backend.app.utils.security import require_roles

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogOut])
def get_audit_logs(
    action: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    recommendation_id: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    current_user: User = Depends(require_roles(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    if user_email:
        q = q.filter(AuditLog.user_email == user_email)
    if recommendation_id:
        q = q.filter(AuditLog.recommendation_id == recommendation_id)

    return q.order_by(AuditLog.timestamp.desc()).limit(limit).all()
