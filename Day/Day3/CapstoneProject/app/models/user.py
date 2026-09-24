from enum import Enum
class UserRole(str,Enum):
    EMPLOYEE = "employee"
    SUPPORT_ENGINEER = "support_engineer"
    TEAM_LEAD = "team_lead"
    ADMIN = "admin"