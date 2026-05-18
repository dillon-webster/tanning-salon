# Tanning Salon Backend Design

Date: 2026-05-06

## Goal

Build a small backend for a tanning salon website using FastAPI and SQLite. The backend supports public client booking, walk-in appointment tracking, salon services, purchasable packages, teeth whitening options, and simple admin management endpoints. Admin endpoints are intentionally unprotected for this class project.

## Technology

- FastAPI for the HTTP API.
- SQLModel for database models, validation, and SQLite persistence.
- SQLite database stored locally as `tanning_salon.db`.
- Pytest with FastAPI `TestClient` and an isolated test SQLite database.

## Domain Model

### Service

Represents an available salon service.

Fields:
- `id`
- `name`
- `category`: `uv_tanning`, `spray_tanning`, or `teeth_whitening`
- `duration_minutes`
- `description`
- `is_active`

### Package

Represents something a client can buy.

Fields:
- `id`
- `service_id`
- `name`
- `package_type`: `pack_5`, `pack_10`, `monthly`, or `single`
- `session_count`
- `valid_days`
- `price_cents`
- `description`
- `is_active`

For monthly packages, `session_count` can be null when usage is unlimited for the active month.

### Client

Represents a customer.

Fields:
- `id`
- `first_name`
- `last_name`
- `email`
- `phone`
- `created_at`

### Staff

Represents a simple staff record for assignment and scheduling.

Fields:
- `id`
- `name`
- `email`
- `phone`
- `is_active`

### Appointment

Represents an online booking or walk-in.

Fields:
- `id`
- `client_id`
- `service_id`
- `package_id`
- `staff_id`
- `appointment_time`
- `duration_minutes`
- `booking_source`: `online` or `walk_in`
- `status`: `scheduled`, `completed`, `cancelled`, or `no_show`
- `notes`
- `created_at`

Appointments prevent overlapping bookings for the same assigned staff member. If no staff member is assigned, the API still allows the booking because this first version does not model individual beds or rooms.

### Purchase

Represents a client buying a package.

Fields:
- `id`
- `client_id`
- `package_id`
- `purchase_date`
- `expires_at`
- `sessions_remaining`
- `is_active`

For monthly packages, `expires_at` is set from `valid_days`. For pack packages, `sessions_remaining` starts from `session_count`.

## API Design

### Public Endpoints

- `GET /services`
  Lists active services.

- `GET /packages`
  Lists active packages. Optional query parameter: `service_id`.

- `POST /clients`
  Creates a client.

- `POST /appointments`
  Books an appointment. The request includes client, service, optional package, appointment time, booking source, optional staff member, and notes.

- `GET /appointments/availability`
  Checks whether a requested appointment time is available for a service and optional staff member.

### Admin Endpoints

Admin endpoints use the `/admin` prefix and have no authentication in this version.

- `/admin/services`
- `/admin/packages`
- `/admin/clients`
- `/admin/staff`
- `/admin/appointments`
- `/admin/purchases`

Each resource supports practical CRUD operations:
- list
- get by id
- create
- update
- delete or deactivate where deletion would remove business history

Services, packages, and staff should be deactivated instead of hard-deleted. Clients, appointments, and purchases can remain in the database for business records.

## Seed Data

On startup, the app seeds initial active services and packages if the database is empty.

Initial services:
- UV Tanning
- Spray Tanning
- Teeth Whitening

Initial packages:
- UV Tanning 5 Pack: $45.00
- UV Tanning 10 Pack: $80.00
- UV Tanning Monthly: $59.00
- Spray Tanning 5 Pack: $120.00
- Spray Tanning 10 Pack: $220.00
- Spray Tanning Monthly: $149.00
- Teeth Whitening Single Session: $79.00
- Teeth Whitening 5 Pack: $350.00

Prices are stored as integer cents and can be edited through admin endpoints.

## Validation And Errors

- Required fields return FastAPI validation errors.
- Missing records return `404`.
- Appointment conflicts return `409`.
- Package and service mismatches return `400`.
- Appointment time must be a valid datetime.
- Duration defaults from the selected service when not provided.

## Testing

Automated tests will cover:
- app health check
- seeded services and packages
- creating clients
- creating public appointments
- preventing overlapping staff appointments
- creating walk-in appointments
- admin CRUD for services and packages
- creating purchases with correct remaining sessions or expiration date

## Out Of Scope

- Login and authentication.
- Payments.
- Real payment receipts.
- Email or SMS reminders.
- Individual tanning beds or rooms.
- Complex staff schedules.
- Package redemption tracking beyond storing purchase session counts.
