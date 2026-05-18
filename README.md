# Tanning Salon Backend

FastAPI + SQLite backend for a tanning salon site. It supports tanning services, teeth whitening, service packages, client records, online bookings, walk-ins, purchases, and API-key protected admin endpoints.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run

```bash
export ADMIN_API_KEY="replace-this-dev-key"
uvicorn app.main:app --reload
```

The app uses `sqlite:///tanning_salon.db` by default. Override it with
`DATABASE_URL` when needed:

```bash
export DATABASE_URL="sqlite:///tanning_salon.db"
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

## Test

Use the project Python module form so imports resolve consistently:

```bash
python3 -m pytest -v
```

## Public Endpoints

- `GET /health`
- `GET /services`
- `GET /packages`
- `GET /packages?service_id=1`
- `POST /clients`
- `POST /appointments`
- `GET /appointments/availability`

Example client:

```json
{
  "first_name": "Avery",
  "last_name": "Stone",
  "email": "avery@example.com",
  "phone": "555-0100"
}
```

Example appointment:

```json
{
  "client_id": 1,
  "service_id": 1,
  "staff_id": 1,
  "appointment_time": "2026-05-07T10:00:00",
  "booking_source": "online",
  "notes": "First visit"
}
```

Use `"booking_source": "walk_in"` for walk-in appointments.

## Admin Endpoints

Admin endpoints require an `X-Admin-API-Key` header matching `ADMIN_API_KEY`.

- `/admin/services`
- `/admin/packages`
- `/admin/clients`
- `/admin/staff`
- `/admin/appointments`
- `/admin/purchases`

Most admin resources support list, get, create, patch, and delete/deactivate actions.

## Seed Data

The app seeds initial data when the SQLite database is empty:

- UV Tanning
- Spray Tanning
- Teeth Whitening
- 5-pack, 10-pack, and monthly tanning packages
- Single-session and 5-pack teeth whitening packages
