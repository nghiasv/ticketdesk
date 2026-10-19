# Software Requirements Specification (SRS) - Stakeholders & User Stories

## 1. List of Stakeholders
* **End-users:** Customer, Support Agent, Manager
* **Decision-maker:** Head of Support Department

## 2. List of User Stories

### US01: As a user, I want to register and log in to the system (via email/password and JWT) to have a secure working session
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Successful registration with valid information
* **Given:** The user does not have an account and is at the registration endpoint.
* **When:** The user submits valid registration information:
    * `email`: RFC 5322 standard, unique in database.
    * `password`: Minimum 8 characters, at least 1 uppercase, 1 number, and 1 special character.
    * `confirm_password`: Matches `password` exactly.
* **Then:**
    * System creates a new record in `Users` table with password hashed via bcrypt/argon2.
    * Default role is assigned as `"Customer"`.
    * System returns HTTP status `201 Created` with a registration success message.

#### Scenario 2: Failed registration due to duplicate email
* **Given:** The email `user@example.com` already exists in the system.
* **When:** A user submits registration with `user@example.com`.
* **Then:** System rejects registration and returns HTTP status `409 Conflict` with message `"This email is already registered"`.

#### Scenario 3: Successful login with valid credentials
* **Given:** An active user account exists in the database.
* **When:** The user submits correct `email` and `password` to `/api/v1/auth/login`.
* **Then:**
    * System returns HTTP status `200 OK`.
    * Response body contains `access_token` (JWT with user ID and role, short-lived), `refresh_token`, and `token_type: "bearer"`.

#### Scenario 4: Failed login due to invalid credentials
* **Given:** The user is on the login page/endpoint.
* **When:** The user submits an unregistered email or an incorrect password.
* **Then:** System rejects request and returns HTTP status `401 Unauthorized` with message `"Invalid email or password"`.

---

### US02: As a Manager, I want to manage accounts and assign roles so that team members have correct permissions
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Manager successfully updates user role
* **Given:** An authenticated user with role `Manager`.
* **When:** The manager sends a `PATCH /api/v1/users/{id}/role` request with `role: "Agent"`.
* **Then:** System updates the user's role in database and returns HTTP status `200 OK`.

#### Scenario 2: Non-manager attempts to change user role
* **Given:** An authenticated user with role `Customer` or `Agent`.
* **When:** The user sends a request to update any user's role.
* **Then:** System denies access and returns HTTP status `403 Forbidden`.

#### Scenario 3: Manager deactivates an account
* **Given:** An authenticated user with role `Manager`.
* **When:** The manager sends a request to deactivate an account (`is_active: false`).
* **Then:**
    * System sets `is_active = false` and revokes all active refresh tokens for that user.
    * System returns HTTP status `200 OK`.

---

### US03: As a user, I want to update my profile and change my password to keep my account secure
* **Priority:** Should Have
* **Acceptance Criteria:**

#### Scenario 1: Successfully update profile information
* **Given:** An authenticated user with a valid JWT access token.
* **When:** The user sends updated `full_name` or `phone_number` to `/api/v1/users/me`.
* **Then:** System updates profile fields in database and returns HTTP status `200 OK`.

#### Scenario 2: Successfully change account password
* **Given:** An authenticated user.
* **When:** The user submits `old_password`, valid `new_password`, and matching `confirm_new_password`.
* **Then:**
    * System validates that `old_password` matches current record.
    * Hashes `new_password`, updates database, and returns HTTP status `200 OK`.

#### Scenario 3: Failed password change due to incorrect old password
* **Given:** An authenticated user.
* **When:** The user submits an incorrect `old_password`.
* **Then:** System rejects change and returns HTTP status `400 Bad Request` with message `"Current password does not match"`.

---

### US04: As a System, I want to intercept unauthenticated or unauthorized requests to secure endpoints
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Request missing Authorization header
* **Given:** A protected API endpoint requiring authentication.
* **When:** A client sends a request without `Authorization: Bearer <token>` header.
* **Then:** System middleware rejects request immediately with HTTP status `401 Unauthorized`.

#### Scenario 2: Request with expired or tampered JWT
* **Given:** A client sends an expired token or one signed with an invalid secret key.
* **When:** The request reaches system auth middleware.
* **Then:** System rejects verification and returns HTTP status `401 Unauthorized` with message `"Token expired or invalid"`.

---

### US05: As a Customer, I want to create a support ticket so that my issue can be resolved
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Customer creates ticket successfully with valid data
* **Given:** An authenticated user with role `Customer`.
* **When:** The user submits `title`, `description`, `category_id`, and `priority` (`Low`, `Medium`, `High`, `Urgent`).
* **Then:**
    * System creates a record in `Tickets` table with status `New`.
    * Automatically populates `created_by` with authenticated user's ID.
    * Generates a unique tracking code (e.g., `TK-202610-0012`).
    * Returns HTTP status `201 Created` with created ticket payload.

#### Scenario 2: Ticket creation fails due to missing mandatory fields
* **Given:** An authenticated user with role `Customer`.
* **When:** The user submits a ticket request with an empty `title` or empty `description`.
* **Then:** System rejects request and returns HTTP status `422 Unprocessable Content` with validation error details.

---

### US06: As a user, I want to list and filter tickets to track processing progress
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Customer lists tickets
* **Given:** An authenticated user with role `Customer`.
* **When:** The user requests `GET /api/v1/tickets`.
* **Then:** System returns HTTP status `200 OK` containing only tickets created by this user.

#### Scenario 2: Agent lists tickets
* **Given:** An authenticated user with role `Agent`.
* **When:** The user requests `GET /api/v1/tickets`.
* **Then:** System returns HTTP status `200 OK` containing tickets assigned to this agent plus unassigned tickets.

#### Scenario 3: Filter tickets by status and pagination
* **Given:** An authenticated user with access to ticket list.
* **When:** The user requests `GET /api/v1/tickets?status=In%20Progress&page=1&page_size=10`.
* **Then:** System returns HTTP status `200 OK` with 10 matching records and pagination metadata (`total`, `page`, `pages`).

---

### US07: As a Manager or Agent, I want to assign tickets to define clear ownership
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Manager assigns an unassigned ticket to an Agent
* **Given:** An authenticated user with role `Manager` and an existing ticket with status `New`.
* **When:** Manager submits `PATCH /api/v1/tickets/{id}/assign` with `agent_id: 5`.
* **Then:**
    * System updates `assigned_to = 5` and transitions status to `Assigned` (or `In Progress`).
    * Returns HTTP status `200 OK`.

#### Scenario 2: Agent claims an unassigned ticket
* **Given:** An authenticated user with role `Agent` and a ticket where `assigned_to` is `NULL`.
* **When:** Agent calls `POST /api/v1/tickets/{id}/claim`.
* **Then:** System assigns the ticket to this agent and returns HTTP status `200 OK`.

#### Scenario 3: Customer attempts to assign a ticket
* **Given:** An authenticated user with role `Customer`.
* **When:** Customer calls ticket assignment endpoint.
* **Then:** System rejects action and returns HTTP status `403 Forbidden`.

---

### US08: As an Agent or Manager, I want to update ticket status to reflect current resolution progress
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Agent marks an in-progress ticket as Resolved
* **Given:** An authenticated `Agent` assigned to the ticket, and the ticket is in status `In Progress`.
* **When:** Agent submits `PATCH /api/v1/tickets/{id}/status` with `status: "Resolved"`.
* **Then:**
    * System updates ticket status to `Resolved` and records `resolved_at = CURRENT_TIMESTAMP`.
    * Returns HTTP status `200 OK`.

#### Scenario 2: Invalid status transition attempted
* **Given:** An existing ticket currently in status `New`.
* **When:** User submits status change directly to `Closed`.
* **Then:** System rejects invalid lifecycle transition and returns HTTP status `400 Bad Request` with message `"Invalid status transition from New to Closed"`.

#### Scenario 3: Updating a closed ticket
* **Given:** An existing ticket currently in status `Closed`.
* **When:** User attempts any status change.
* **Then:** System rejects change and returns HTTP status `400 Bad Request` with message `"Closed tickets cannot be modified"`.

---

### US09: As a user, I want to comment on a ticket to discuss and share details
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Successfully post a public comment
* **Given:** An authenticated user who is either the ticket owner, assigned agent, or a manager.
* **When:** The user sends a `POST /api/v1/tickets/{id}/comments` request with non-empty `content` and `is_internal: false`.
* **Then:** System saves comment record and returns HTTP status `201 Created` with comment details.

#### Scenario 2: Agent posts an internal note
* **Given:** An authenticated user with role `Agent` or `Manager`.
* **When:** User submits a comment with `is_internal: true`.
* **Then:**
    * System stores comment with internal flag.
    * Returns HTTP status `201 Created`.
    * Customer queries will omit this comment from response.

#### Scenario 3: Customer attempts to read internal notes
* **Given:** An authenticated user with role `Customer`.
* **When:** User queries `GET /api/v1/tickets/{id}/comments`.
* **Then:** System returns HTTP status `200 OK` containing only comments where `is_internal == false`.

---

### US10: As a user or Manager, I want to view ticket activity history to trace changes over time
* **Priority:** Should Have
* **Acceptance Criteria:**

#### Scenario 1: Audit entry created automatically upon ticket update
* **Given:** An existing ticket.
* **When:** An authorized user updates ticket status or reassigns agent.
* **Then:** System automatically writes an immutable log to `TicketActivities` containing `ticket_id`, `actor_id`, `action`, `old_value`, `new_value`, and timestamp.

#### Scenario 2: Retrieve activity timeline
* **Given:** An authenticated user authorized to view the ticket.
* **When:** The user requests `GET /api/v1/tickets/{id}/activities`.
* **Then:** System returns HTTP status `200 OK` with activities sorted chronologically descending.

---

### US11: As a user, I want to upload file attachments to provide visual evidence for issues
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Upload attachment with valid format and size
* **Given:** An authorized user and an active ticket.
* **When:** The user uploads a file (`.png`, `.jpg`, `.pdf`, `.docx`) with size <= 10MB.
* **Then:**
    * System stores file with a UUID-based filename.
    * Creates record in `Attachments` linked to `ticket_id`.
    * Returns HTTP status `201 Created` with attachment metadata and download URL.

#### Scenario 2: Upload fails due to unsupported file format
* **Given:** An authorized user.
* **When:** User attempts to upload an executable file (e.g., `payload.exe` or `script.sh`).
* **Then:** System rejects file and returns HTTP status `400 Bad Request` with message `"Unsupported file type"`.

#### Scenario 3: Upload fails due to file size limit exceeded
* **Given:** An authorized user.
* **When:** User uploads a file with size exceeding 10MB.
* **Then:** System rejects upload and returns HTTP status `413 Payload Too Large`.

---

### US12: As a user, I want to download attachments securely
* **Priority:** Should Have
* **Acceptance Criteria:**

#### Scenario 1: Authorized user downloads file
* **Given:** An authenticated user associated with the ticket (owner, assigned agent, or manager).
* **When:** User sends `GET /api/v1/attachments/{id}/download`.
* **Then:** System returns file stream with HTTP status `200 OK` and correct `Content-Disposition` header.

#### Scenario 2: Unauthorized user attempts to download file
* **Given:** An authenticated user with no association to the ticket.
* **When:** User sends `GET /api/v1/attachments/{id}/download`.
* **Then:** System denies access and returns HTTP status `403 Forbidden`.

---

### US13: As a Customer, I want to receive an email notification when my ticket is created
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Email dispatched asynchronously on ticket creation
* **Given:** A customer successfully creates a new ticket.
* **When:** The ticket record is committed to database.
* **Then:**
    * System enqueues a Celery task `send_ticket_created_email`.
    * API response completes immediately without waiting for SMTP network roundtrip.
    * Background worker sends email containing ticket code and direct URL.

#### Scenario 2: Background worker handling SMTP delivery failure
* **Given:** Celery task is executing email delivery.
* **When:** SMTP server is temporarily unreachable.
* **Then:** Celery task retries delivery automatically up to 3 times using exponential backoff before logging failure.

---

### US14: As an Agent, I want to receive an email when a ticket is assigned to me
* **Priority:** Should Have
* **Acceptance Criteria:**

#### Scenario 1: Assignment trigger dispatches notification
* **Given:** An existing ticket.
* **When:** Manager assigns this ticket to an Agent (`assigned_to` changes).
* **Then:**
    * System queues a background Celery task.
    * Agent receives notification email containing ticket priority, title, and direct link.

---

### US15: As a Manager, I want to view a ticket status overview dashboard to monitor workload
* **Priority:** Should Have
* **Acceptance Criteria:**

#### Scenario 1: Manager retrieves dashboard overview metrics
* **Given:** An authenticated user with role `Manager`.
* **When:** User requests `GET /api/v1/dashboard/overview?start_date=2026-10-01&end_date=2026-10-19`.
* **Then:**
    * System returns HTTP status `200 OK`.
    * Payload includes counts grouped by status (`new_count`, `in_progress_count`, `resolved_count`, `closed_count`) and `unassigned_count`.

#### Scenario 2: Non-manager attempts to access dashboard
* **Given:** An authenticated user with role `Customer` or `Agent`.
* **When:** User requests `GET /api/v1/dashboard/overview`.
* **Then:** System returns HTTP status `403 Forbidden`.

---

### US16: As a Manager, I want to view Agent performance metrics to evaluate efficiency
* **Priority:** Should Have
* **Acceptance Criteria:**

#### Scenario 1: Retrieve agent performance stats
* **Given:** An authenticated user with role `Manager`.
* **When:** User requests `GET /api/v1/dashboard/agents-performance`.
* **Then:**
    * System returns HTTP status `200 OK`.
    * Payload contains list of agents with: `tickets_assigned`, `tickets_resolved`, and `avg_resolution_time_hours`.

---

### US17: As a Manager, I want tickets exceeding SLA thresholds to be flagged for timely intervention
* **Priority:** Could Have
* **Acceptance Criteria:**

#### Scenario 1: Ticket breaches SLA threshold
* **Given:** A ticket with `priority: "Urgent"` (SLA: 4 hours) is in status `In Progress`.
* **When:** Elapsed time since creation exceeds 4 hours without moving to `Resolved`.
* **Then:**
    * Background periodic task marks `is_sla_breached = true`.
    * Ticket appears in dashboard filter `GET /api/v1/tickets?sla_breached=true`.

---

### US18: As a Manager, I want to export tickets to Excel in the background so large reports do not block the UI
* **Priority:** Should Have
* **Acceptance Criteria:**

#### Scenario 1: Manager requests async Excel report export
* **Given:** An authenticated user with role `Manager`.
* **When:** User posts filter parameters to `POST /api/v1/reports/tickets/export`.
* **Then:**
    * System triggers Celery task `generate_excel_report`.
    * API immediately returns HTTP status `202 Accepted` with `task_id`.

#### Scenario 2: Export task finishes generation
* **Given:** Celery worker finishes generating `.xlsx` spreadsheet.
* **When:** Task execution completes successfully.
* **Then:** System stores file temporarily on disk/cloud storage and marks task status as `SUCCESS` with download URI.

---

### US19: As a Manager, I want to poll export task status and download the generated Excel file
* **Priority:** Should Have
* **Acceptance Criteria:**

#### Scenario 1: Poll export task status while pending
* **Given:** A valid `task_id` for an ongoing export job.
* **When:** Manager requests `GET /api/v1/reports/tasks/{task_id}`.
* **Then:** System returns HTTP status `200 OK` with `status: "PENDING"` (or `"PROCESSING"`).

#### Scenario 2: Download completed Excel report
* **Given:** An export task with status `SUCCESS`.
* **When:** Manager accesses returned download URL.
* **Then:** System returns file stream with HTTP status `200 OK` and Content-Type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.

---

### US20: As a Client Developer, I want standardized JSON envelopes and consistent pagination
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Standardized response envelope on success
* **Given:** A client calls any successful API endpoint.
* **When:** Server returns response.
* **Then:** Body matches format:
  ```json
  {
    "success": true,
    "data": {},
    "message": "Operation successful",
    "errors": null
  }
  ```

#### Scenario 2: Standardized error envelope on failure
* **Given:** A client sends a malformed or unauthorized request.
* **When:** Server rejects request.
* **Then:** Response envelope matches:
  ```json
  {
    "success": false,
    "data": null,
    "message": "Error description",
    "errors": [ { "field": "email", "message": "Invalid format" } ]
  }
  ```

---

### US21: As a Developer and QA Tester, I want interactive Swagger documentation to test endpoints directly
* **Priority:** Must Have
* **Acceptance Criteria:**

#### Scenario 1: Access Swagger UI documentation
* **Given:** System API server is running.
* **When:** User navigates to `/docs` in browser.
* **Then:**
    * Interactive Swagger UI loads with endpoints grouped by tags (`Auth`, `Users`, `Tickets`, `Comments`, `Dashboard`, `Reports`).
    * Each endpoint displays description, path parameters, request body schemas, and response codes.

#### Scenario 2: Execute authenticated request from Swagger UI
* **Given:** User has a valid JWT access token.
* **When:** User clicks `Authorize` button, inputs `Bearer <token>`, and executes a protected endpoint.
* **Then:** Swagger UI attaches header properly and displays live HTTP response and status code.