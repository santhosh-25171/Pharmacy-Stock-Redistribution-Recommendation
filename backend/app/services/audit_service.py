"""
Audit Logging Service.
Records immutable historical events for compliance, accountability, and traceability.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models import AuditLog

def log_audit_event(
    db: Session,
    user_id: Optional[int],
    user_email: str,
    user_role: str,
    action: str,
    recommendation_id: Optional[str] = None,
    previous_state: Optional[str] = None,
    new_state: Optional[str] = None,
    quantity: Optional[int] = None,
    source_pharmacy_id: Optional[str] = None,
    destination_pharmacy_id: Optional[str] = None,
    reason: Optional[str] = None
) -> AuditLog:
    """
    Creates and commits an audit log record.
    """
    audit = AuditLog(
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        recommendation_id=recommendation_id,
        action=action,
        previous_state=previous_state,
        new_state=new_state,
        quantity=quantity,
        source_pharmacy_id=source_pharmacy_id,
        destination_pharmacy_id=destination_pharmacy_id,
        reason=reason,
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
