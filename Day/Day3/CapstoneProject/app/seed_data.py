# scripts/seed_data.py

# use it_servicedesk
# db.users.deleteMany({})
# db.categories.deleteMany({})
# db.tickets.deleteMany({})
# db.comments.deleteMany({})
# db.attachments.deleteMany({})
# db.audit_logs.deleteMany({})
#
# Purpose:
#   Populates MongoDB with sample data for every entity (User, Category,
#   Ticket, Comment, Attachment, AuditLog) — at least 8 records each —
#   with realistic cross-references (a ticket's category_id points to a
#   real category, a comment's ticket_id points to a real ticket, etc.),
#   so the API and frontend have something meaningful to show right away.
#
# This is a one-off maintenance script, not part of the running API, which
# is why it lives in scripts/ instead of app/. It reuses the exact same
# shared MongoDB connection as the app itself (app/database.py) so it
# writes to the same database the API reads from.
#
# Run it from the backend project root with:
#   python -m scripts.seed_data
#
# WARNING: this clears the 6 collections below before inserting, so it's
# meant for a fresh/dev database, not production data.

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Allows running this script directly (python scripts/seed_data.py) by
# putting the project root on the import path, so "from app...." works
# the same way it does for the app itself.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import database  # the same shared connection app/database.py builds

# ---------------------------------------------------------------------------
# IDs are plain, readable strings (not real uuid4 values) on purpose — the
# app's schemas only require "id" to be a string, they never validate uuid
# *format*. Readable ids make it far easier to see how records cross-reference
# each other in this seed file.
# ---------------------------------------------------------------------------

NOW = datetime.utcnow()


def days_ago(n: int) -> datetime:
    """Small helper so seeded timestamps look realistic and spread out."""
    return NOW - timedelta(days=n)


# --- 1. Users (8) — covering all four roles ---------------------------------
USERS = [
    {"id": "user-emp-1", "name": "Priya Sharma", "email": "priya.sharma@company.com",
     "password": "password123", "role": "employee", "created_at": days_ago(30)},
    {"id": "user-emp-2", "name": "Rahul Verma", "email": "rahul.verma@company.com",
     "password": "password123", "role": "employee", "created_at": days_ago(29)},
    {"id": "user-emp-3", "name": "Ananya Gupta", "email": "ananya.gupta@company.com",
     "password": "password123", "role": "employee", "created_at": days_ago(28)},
    {"id": "user-emp-4", "name": "Karan Mehta", "email": "karan.mehta@company.com",
     "password": "password123", "role": "employee", "created_at": days_ago(27)},
    {"id": "user-lead-1", "name": "Neha Singh", "email": "neha.singh@company.com",
     "password": "password123", "role": "team_lead", "created_at": days_ago(60)},
    {"id": "user-support-1", "name": "Arjun Nair", "email": "arjun.nair@company.com",
     "password": "password123", "role": "support_engineer", "created_at": days_ago(50)},
    {"id": "user-support-2", "name": "Divya Iyer", "email": "divya.iyer@company.com",
     "password": "password123", "role": "support_engineer", "created_at": days_ago(45)},
    {"id": "user-admin-1", "name": "Vikram Rao", "email": "vikram.rao@company.com",
     "password": "password123", "role": "admin", "created_at": days_ago(90)},
]

# --- 2. Categories (8) -------------------------------------------------------
CATEGORIES = [
    {"id": "cat-laptop", "name": "Laptop", "description": "Laptop hardware issues", "created_at": days_ago(90)},
    {"id": "cat-desktop", "name": "Desktop", "description": "Desktop hardware issues", "created_at": days_ago(90)},
    {"id": "cat-network", "name": "Network", "description": "Wired/Wi-Fi connectivity issues", "created_at": days_ago(90)},
    {"id": "cat-vpn", "name": "VPN Access", "description": "VPN connection and access issues", "created_at": days_ago(90)},
    {"id": "cat-software", "name": "Software Installation", "description": "Installing or updating software", "created_at": days_ago(90)},
    {"id": "cat-email", "name": "Email & Outlook", "description": "Mailbox and Outlook client issues", "created_at": days_ago(90)},
    {"id": "cat-printer", "name": "Printer", "description": "Printer and scanning issues", "created_at": days_ago(90)},
    {"id": "cat-mobile", "name": "Mobile Device", "description": "Company phone/tablet issues", "created_at": days_ago(90)},
]

# --- 3. Tickets (8) — spans every lifecycle status at least once -------------
TICKETS = [
    {"id": "ticket-1", "title": "Laptop won't turn on", "description": "Screen stays black on power button press.",
     "category_id": "cat-laptop", "status": "new", "created_by": "user-emp-1", "assigned_to": None,
     "created_at": days_ago(6), "updated_at": days_ago(6)},
    {"id": "ticket-2", "title": "Cannot connect to office Wi-Fi", "description": "Laptop drops Wi-Fi every few minutes.",
     "category_id": "cat-network", "status": "assigned", "created_by": "user-emp-2", "assigned_to": "user-support-1",
     "created_at": days_ago(5), "updated_at": days_ago(4)},
    {"id": "ticket-3", "title": "VPN times out on connect", "description": "VPN client times out after entering credentials.",
     "category_id": "cat-vpn", "status": "in_progress", "created_by": "user-emp-3", "assigned_to": "user-support-2",
     "created_at": days_ago(5), "updated_at": days_ago(3)},
    {"id": "ticket-4", "title": "Need Photoshop installed", "description": "Design team requires Photoshop for a project.",
     "category_id": "cat-software", "status": "on_hold", "created_by": "user-emp-4", "assigned_to": "user-support-1",
     "created_at": days_ago(4), "updated_at": days_ago(2)},
    {"id": "ticket-5", "title": "Printer jams on double-sided printing", "description": "3rd floor printer jams every time on duplex mode.",
     "category_id": "cat-printer", "status": "resolved", "created_by": "user-emp-1", "assigned_to": "user-support-2",
     "created_at": days_ago(10), "updated_at": days_ago(1)},
    {"id": "ticket-6", "title": "Outlook not syncing new emails", "description": "New emails aren't appearing until a manual refresh.",
     "category_id": "cat-email", "status": "closed", "created_by": "user-emp-2", "assigned_to": "user-support-1",
     "created_at": days_ago(12), "updated_at": days_ago(1)},
    {"id": "ticket-7", "title": "Company phone won't charge", "description": "Phone doesn't charge with the supplied cable.",
     "category_id": "cat-mobile", "status": "new", "created_by": "user-emp-3", "assigned_to": None,
     "created_at": days_ago(1), "updated_at": days_ago(1)},
    {"id": "ticket-8", "title": "Desktop running very slow", "description": "Desktop takes 10+ minutes to boot up.",
     "category_id": "cat-desktop", "status": "assigned", "created_by": "user-emp-4", "assigned_to": "user-support-2",
     "created_at": days_ago(2), "updated_at": days_ago(1)},
]

# --- 4. Comments (8) — spread across several tickets -------------------------
COMMENTS = [
    {"id": "comment-1", "ticket_id": "ticket-1", "author_id": "user-emp-1",
     "content": "Tried holding power for 30 seconds, still nothing.", "created_at": days_ago(6)},
    {"id": "comment-2", "ticket_id": "ticket-2", "author_id": "user-support-1",
     "content": "Can you share which Wi-Fi network you're connecting to?", "created_at": days_ago(4)},
    {"id": "comment-3", "ticket_id": "ticket-2", "author_id": "user-emp-2",
     "content": "It's the main office network, 5GHz band.", "created_at": days_ago(4)},
    {"id": "comment-4", "ticket_id": "ticket-3", "author_id": "user-support-2",
     "content": "Looking into the VPN gateway logs now.", "created_at": days_ago(3)},
    {"id": "comment-5", "ticket_id": "ticket-4", "author_id": "user-emp-4",
     "content": "Any update on the license approval?", "created_at": days_ago(2)},
    {"id": "comment-6", "ticket_id": "ticket-5", "author_id": "user-support-2",
     "content": "Replaced the duplex unit, please confirm it's fixed.", "created_at": days_ago(1)},
    {"id": "comment-7", "ticket_id": "ticket-6", "author_id": "user-emp-2",
     "content": "Confirmed, syncing normally now. Thank you!", "created_at": days_ago(1)},
    {"id": "comment-8", "ticket_id": "ticket-8", "author_id": "user-support-2",
     "content": "Running a disk cleanup and startup audit.", "created_at": days_ago(1)},
]

# --- 5. Attachments (8) — metadata only, spread across several tickets -------
ATTACHMENTS = [
    {"id": "attachment-1", "ticket_id": "ticket-1", "uploaded_by": "user-emp-1",
     "filename": "laptop_screen.png", "url": "https://files.example.com/laptop_screen.png",
     "size": 204800, "created_at": days_ago(6)},
    {"id": "attachment-2", "ticket_id": "ticket-2", "uploaded_by": "user-support-1",
     "filename": "wifi_error_log.txt", "url": "https://files.example.com/wifi_error_log.txt",
     "size": 5120, "created_at": days_ago(4)},
    {"id": "attachment-3", "ticket_id": "ticket-3", "uploaded_by": "user-emp-3",
     "filename": "vpn_timeout.png", "url": "https://files.example.com/vpn_timeout.png",
     "size": 153600, "created_at": days_ago(5)},
    {"id": "attachment-4", "ticket_id": "ticket-4", "uploaded_by": "user-emp-4",
     "filename": "license_request.pdf", "url": "https://files.example.com/license_request.pdf",
     "size": 81920, "created_at": days_ago(4)},
    {"id": "attachment-5", "ticket_id": "ticket-5", "uploaded_by": "user-support-2",
     "filename": "printer_jam_photo.jpg", "url": "https://files.example.com/printer_jam_photo.jpg",
     "size": 512000, "created_at": days_ago(9)},
    {"id": "attachment-6", "ticket_id": "ticket-6", "uploaded_by": "user-emp-2",
     "filename": "outlook_sync_screenshot.png", "url": "https://files.example.com/outlook_sync_screenshot.png",
     "size": 174080, "created_at": days_ago(12)},
    {"id": "attachment-7", "ticket_id": "ticket-7", "uploaded_by": "user-emp-3",
     "filename": "charging_port_photo.jpg", "url": "https://files.example.com/charging_port_photo.jpg",
     "size": 245760, "created_at": days_ago(1)},
    {"id": "attachment-8", "ticket_id": "ticket-8", "uploaded_by": "user-support-2",
     "filename": "startup_report.pdf", "url": "https://files.example.com/startup_report.pdf",
     "size": 92160, "created_at": days_ago(1)},
]

# --- 6. Audit logs (8) — matching real actions taken on the tickets above ----
AUDIT_LOGS = [
    {"id": "audit-1", "ticket_id": "ticket-1", "action": "created", "performed_by": "user-emp-1",
     "details": "Ticket created with status 'new'.", "created_at": days_ago(6)},
    {"id": "audit-2", "ticket_id": "ticket-2", "action": "created", "performed_by": "user-emp-2",
     "details": "Ticket created with status 'new'.", "created_at": days_ago(5)},
    {"id": "audit-3", "ticket_id": "ticket-2", "action": "assigned", "performed_by": "user-lead-1",
     "details": "Assigned to user 'user-support-1'. Status moved from 'new' to 'assigned'.", "created_at": days_ago(4)},
    {"id": "audit-4", "ticket_id": "ticket-3", "action": "created", "performed_by": "user-emp-3",
     "details": "Ticket created with status 'new'.", "created_at": days_ago(5)},
    {"id": "audit-5", "ticket_id": "ticket-3", "action": "assigned", "performed_by": "user-lead-1",
     "details": "Assigned to user 'user-support-2'. Status moved from 'new' to 'assigned'.", "created_at": days_ago(4)},
    {"id": "audit-6", "ticket_id": "ticket-3", "action": "status_changed", "performed_by": "user-support-2",
     "details": "Status changed from 'assigned' to 'in_progress'.", "created_at": days_ago(3)},
    {"id": "audit-7", "ticket_id": "ticket-5", "action": "status_changed", "performed_by": "user-support-2",
     "details": "Status changed from 'in_progress' to 'resolved'.", "created_at": days_ago(1)},
    {"id": "audit-8", "ticket_id": "ticket-6", "action": "status_changed", "performed_by": "user-emp-2",
     "details": "Status changed from 'resolved' to 'closed'.", "created_at": days_ago(1)},
]


def seed() -> None:
    """Clears the 6 collections and inserts the fixed seed data above."""
    collections_and_data = [
        ("users", USERS),
        ("categories", CATEGORIES),
        ("tickets", TICKETS),
        ("comments", COMMENTS),
        ("attachments", ATTACHMENTS),
        ("audit_logs", AUDIT_LOGS),
    ]

    for collection_name, documents in collections_and_data:
        collection = database[collection_name]
        deleted = collection.delete_many({}).deleted_count
        collection.insert_many(documents)
        print(f"{collection_name}: cleared {deleted} old record(s), inserted {len(documents)} new record(s)")


if __name__ == "__main__":
    seed()
    print("\nSeeding complete.")