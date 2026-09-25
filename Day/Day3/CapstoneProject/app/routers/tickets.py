# app/routers/tickets.py
#
# Purpose:
#   HTTP endpoints for the Ticket entity — the core entity of this system.
#   GET    /tickets                  -> list all tickets (supports filtering + pagination)
#   GET    /tickets/{id}             -> read one ticket
#   POST   /tickets                  -> create a ticket (Employee raises an issue)
#   PUT    /tickets/{id}             -> update ticket details (title/description/category)
#   PATCH  /tickets/{id}/assign      -> assign/reassign a technician (Team Lead)
#   PATCH  /tickets/{id}/status      -> move the ticket through its lifecycle
#   DELETE /tickets/{id}             -> remove a ticket
#
# Same ID pattern as previous entities: each document has a self-generated
# UUID string "id" instead of relying on MongoDB's ObjectId.

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.collection import Collection

from app.dependencies import (
    get_tickets_collection,
    get_categories_collection,
    get_users_collection,
    get_audit_logs_collection,
)
from app.models.ticket import TicketStatus, is_valid_transition
from app.models.audit_log import AuditAction, build_audit_log_doc
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketAssign,
    TicketStatusUpdate,
    TicketResponse,
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    tickets_collection: Collection = Depends(get_tickets_collection),
    categories_collection: Collection = Depends(get_categories_collection),
    users_collection: Collection = Depends(get_users_collection),
    audit_logs_collection: Collection = Depends(get_audit_logs_collection),
):
    """
    Create a new ticket.
    POST -> create, per REST convention.
    Every new ticket always starts at status NEW and unassigned — the client
    cannot set these directly, which is why they aren't fields on TicketCreate.
    """
    # Data-integrity checks: the referenced category and user must actually exist.
    if not categories_collection.find_one({"id": payload.category_id}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id does not match any existing category.",
        )
    if not users_collection.find_one({"id": payload.created_by}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="created_by does not match any existing user.",
        )

    now = datetime.utcnow()
    ticket_doc = {
        "id": str(uuid4()),
        "title": payload.title,
        "description": payload.description,
        "category_id": payload.category_id,
        "status": TicketStatus.NEW,
        "created_by": payload.created_by,
        "assigned_to": None,
        "created_at": now,
        "updated_at": now,
    }
    tickets_collection.insert_one(ticket_doc)

    # Record this creation in the audit trail.
    audit_logs_collection.insert_one(
        build_audit_log_doc(
            ticket_id=ticket_doc["id"],
            action=AuditAction.CREATED,
            performed_by=payload.created_by,
            details=f"Ticket created with status '{TicketStatus.NEW.value}'.",
        )
    )
    return ticket_doc


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    tickets_collection: Collection = Depends(get_tickets_collection),
    # --- Query parameters: all optional, used to filter/control the request ---
    status_filter: Optional[TicketStatus] = Query(default=None, alias="status", description="Filter by exact status"),
    category_id: Optional[str] = Query(default=None, description="Filter by category id"),
    assigned_to: Optional[str] = Query(default=None, description="Filter by assigned technician's user id"),
    created_by: Optional[str] = Query(default=None, description="Filter by the employee who raised the ticket"),
    skip: int = Query(default=0, ge=0, description="Number of tickets to skip (for pagination)"),
    limit: int = Query(default=20, ge=1, le=100, description="Max number of tickets to return (1-100)"),
):
    """
    List tickets, with optional filtering and pagination.
    GET -> read, per REST convention.

    Examples:
      GET /tickets                                -> first 20 tickets
      GET /tickets?status=in_progress              -> only in-progress tickets
      GET /tickets?category_id=<id>&limit=50       -> up to 50 tickets in one category
      GET /tickets?assigned_to=<id>&skip=20&limit=20 -> a technician's tickets, page 2
    """
    # Build the MongoDB filter dict from whichever query parameters were actually provided.
    mongo_filter = {}
    if status_filter is not None:
        mongo_filter["status"] = status_filter
    if category_id is not None:
        mongo_filter["category_id"] = category_id
    if assigned_to is not None:
        mongo_filter["assigned_to"] = assigned_to
    if created_by is not None:
        mongo_filter["created_by"] = created_by

    cursor = tickets_collection.find(mongo_filter).sort("created_at", -1).skip(skip).limit(limit)
    return list(cursor)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: str,
    tickets_collection: Collection = Depends(get_tickets_collection),
):
    """Get a single ticket by id ("ticket_id" is a path parameter)."""
    ticket_doc = tickets_collection.find_one({"id": ticket_id})
    if not ticket_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket_doc


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: str,
    payload: TicketUpdate,
    tickets_collection: Collection = Depends(get_tickets_collection),
    categories_collection: Collection = Depends(get_categories_collection),
):
    """
    Update ticket details (title/description/category) only.
    Status and assignment are changed through their own dedicated endpoints
    below, so this endpoint deliberately does not touch them.
    """
    existing = tickets_collection.find_one({"id": ticket_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return existing

    if "category_id" in update_data and not categories_collection.find_one({"id": update_data["category_id"]}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id does not match any existing category.",
        )

    update_data["updated_at"] = datetime.utcnow()
    tickets_collection.update_one({"id": ticket_id}, {"$set": update_data})
    return tickets_collection.find_one({"id": ticket_id})


@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: str,
    payload: TicketAssign,
    tickets_collection: Collection = Depends(get_tickets_collection),
    users_collection: Collection = Depends(get_users_collection),
    audit_logs_collection: Collection = Depends(get_audit_logs_collection),
):
    """
    Assign or reassign a technician to a ticket (Team Lead responsibility).

    Lifecycle rule applied here: assigning a technician to a brand-new ticket
    naturally moves it from NEW -> ASSIGNED. If the ticket is being
    *reassigned* later on (already past NEW), we only change the technician
    and leave the current status untouched — reassignment shouldn't reset
    progress that's already been made.
    """
    existing = tickets_collection.find_one({"id": ticket_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if not users_collection.find_one({"id": payload.assigned_to}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="assigned_to does not match any existing user.",
        )
    if not users_collection.find_one({"id": payload.assigned_by}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="assigned_by does not match any existing user.",
        )

    update_data = {"assigned_to": payload.assigned_to, "updated_at": datetime.utcnow()}

    status_also_changed = existing["status"] == TicketStatus.NEW
    if status_also_changed:
        update_data["status"] = TicketStatus.ASSIGNED

    tickets_collection.update_one({"id": ticket_id}, {"$set": update_data})

    # Record this assignment in the audit trail.
    details = f"Assigned to user '{payload.assigned_to}'."
    if status_also_changed:
        details += f" Status moved from '{TicketStatus.NEW.value}' to '{TicketStatus.ASSIGNED.value}'."
    audit_logs_collection.insert_one(
        build_audit_log_doc(
            ticket_id=ticket_id,
            action=AuditAction.ASSIGNED,
            performed_by=payload.assigned_by,
            details=details,
        )
    )
    return tickets_collection.find_one({"id": ticket_id})


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: str,
    payload: TicketStatusUpdate,
    tickets_collection: Collection = Depends(get_tickets_collection),
    users_collection: Collection = Depends(get_users_collection),
    audit_logs_collection: Collection = Depends(get_audit_logs_collection),
):
    """
    Move a ticket through its lifecycle.
    Enforces the ALLOWED_TRANSITIONS rules from app/models/ticket.py —
    e.g. a ticket cannot jump straight from NEW to RESOLVED, and nothing
    can leave CLOSED once it gets there.
    """
    existing = tickets_collection.find_one({"id": ticket_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if not users_collection.find_one({"id": payload.changed_by}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="changed_by does not match any existing user.",
        )

    current_status = TicketStatus(existing["status"])
    new_status = payload.status

    if not is_valid_transition(current_status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot move ticket from '{current_status.value}' to '{new_status.value}'.",
        )

    tickets_collection.update_one(
        {"id": ticket_id},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow()}},
    )

    # Record this status change in the audit trail.
    audit_logs_collection.insert_one(
        build_audit_log_doc(
            ticket_id=ticket_id,
            action=AuditAction.STATUS_CHANGED,
            performed_by=payload.changed_by,
            details=f"Status changed from '{current_status.value}' to '{new_status.value}'.",
        )
    )
    return tickets_collection.find_one({"id": ticket_id})


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: str,
    tickets_collection: Collection = Depends(get_tickets_collection),
):
    """Delete a ticket by id. DELETE -> remove, per REST convention."""
    result = tickets_collection.delete_one({"id": ticket_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return None