# app/routers/audit_logs.py
#
# Purpose:
#   Read-only HTTP endpoints for the AuditLog entity.
#   GET /audit-logs                       -> list every audit log entry in the system
#   GET /tickets/{ticket_id}/audit-logs   -> list audit log entries for one ticket
#
# There is intentionally no POST/PUT/DELETE here — entries are only ever
# written by app/routers/tickets.py when a ticket is created, assigned, or
# changes status.

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.dependencies import get_audit_logs_collection, get_tickets_collection
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(tags=["Audit Logs"])


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_all_audit_logs(audit_logs_collection: Collection = Depends(get_audit_logs_collection)):
    """List every audit log entry, most recent first."""
    return list(audit_logs_collection.find().sort("created_at", -1))


@router.get("/tickets/{ticket_id}/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs_for_ticket(
    ticket_id: str,
    audit_logs_collection: Collection = Depends(get_audit_logs_collection),
    tickets_collection: Collection = Depends(get_tickets_collection),
):
    """List the audit trail for one specific ticket, oldest first (a readable history)."""
    if not tickets_collection.find_one({"id": ticket_id}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return list(audit_logs_collection.find({"ticket_id": ticket_id}).sort("created_at", 1))