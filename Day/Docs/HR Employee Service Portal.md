HR Employee Service Portal

Requests such as:

* Leave clarification
* Payroll query
* Experience letter
* Asset request
* Onboarding request

---

# 5. `HR Employee Service Portal`

An organization has employees who raise HR-related service requests for leave, payroll, documents, assets, and onboarding services.

Example:

> Employee → raises HR service request → HR Service Desk → assigns HR staff → HR staff processes it → resolves → employee confirms → request closed.

### Main actors

| Role         | Responsibilities                                        |
| ------------ | ------------------------------------------------------- |
| Employee     | Create and view own requests                            |
| HR Executive | View assigned requests, process requests, update status |
| HR Manager   | Assign/reassign requests, monitor HR team               |
| Admin        | Manage users, categories, departments, configuration    |

### Core entities

```text
User

ServiceRequest

Category

Comment

Attachment

AuditLog
```

### Request categories

```text
LEAVE_CLARIFICATION
PAYROLL_QUERY
EXPERIENCE_LETTER
ASSET_REQUEST
ONBOARDING_REQUEST
```

### Request lifecycle

```text
NEW
  ↓
ASSIGNED
  ↓
IN_PROGRESS
  ↓
RESOLVED
  ↓
CLOSED
```

with possible:

```text
IN_PROGRESS → ON_HOLD
ON_HOLD → IN_PROGRESS
```

### Example — Experience Letter

```text
Employee
   ↓
Raises "Experience Letter" request
   ↓
HR Service Desk
   ↓
Assigns to HR Executive
   ↓
HR Executive verifies employee details
   ↓
Generates Experience Letter
   ↓
RESOLVED
   ↓
Employee receives/confirms document
   ↓
CLOSED
```

### Example — Payroll Query

```text
Employee
   ↓
Raises "Payroll Query"
   ↓
HR Service Desk
   ↓
Assigns to Payroll Staff
   ↓
Payroll Staff investigates salary/payroll details
   ↓
Provides clarification
   ↓
RESOLVED
   ↓
Employee confirms
   ↓
CLOSED
```

### Example — Onboarding Request

```text
New Employee
      ↓
Raises / receives "Onboarding Request"
      ↓
HR Service Desk
      ↓
Assigns to HR Executive
      ↓
HR completes onboarding activities
      ↓
RESOLVED
      ↓
Employee confirms
      ↓
CLOSED
```

**App 5 introduces an important enterprise concept:** requests may involve **documents and employee-specific information**, making `Attachment`, `AuditLog`, and role-based access particularly important.