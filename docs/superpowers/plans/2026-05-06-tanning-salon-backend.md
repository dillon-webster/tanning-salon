# Tanning Salon Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI + SQLite backend for tanning services, package sales, online bookings, walk-ins, teeth whitening, and simple admin management.

**Architecture:** Use SQLModel models for persistence and validation, one FastAPI app factory, dependency-injected database sessions, and route modules for public and admin APIs. Keep the backend self-contained so it can run locally with SQLite and be tested with an isolated temporary SQLite database.

**Tech Stack:** Python, FastAPI, SQLModel, SQLite, pytest, FastAPI TestClient, uvicorn.

---

## File Structure

- `requirements.txt`: Python dependencies.
- `README.md`: setup, run, and test commands.
- `app/__init__.py`: package marker.
- `app/database.py`: engine/session helpers, database initialization, seed-data entry point.
- `app/models.py`: SQLModel table models and enums.
- `app/schemas.py`: request and response models.
- `app/seed.py`: deterministic starter services and packages.
- `app/services.py`: reusable business logic for records, appointment conflicts, purchases, and availability.
- `app/routes_public.py`: public client-facing routes.
- `app/routes_admin.py`: simple unprotected admin CRUD routes.
- `app/main.py`: FastAPI app creation and router registration.
- `tests/conftest.py`: isolated test app and database setup.
- `tests/test_public_api.py`: public endpoint behavior tests.
- `tests/test_admin_api.py`: admin endpoint behavior tests.
- `tests/test_purchases.py`: purchase business-rule tests.

## Task 1: Project Scaffold And Health Check

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `app/__init__.py`
- Create: `app/database.py`
- Create: `app/main.py`
- Create: `tests/conftest.py`
- Create: `tests/test_public_api.py`

- [ ] **Step 1: Write the failing health-check test**

Add this to `tests/conftest.py`:

```python
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import create_app


def get_test_client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    app = create_app(seed_database=False)

    def override_get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as client:
        yield client
```

Add this to `tests/test_public_api.py`:

```python
def test_health_check_returns_ok(get_test_client):
    client = next(get_test_client)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_public_api.py::test_health_check_returns_ok -v`

Expected: FAIL because `app.database` and `app.main` do not exist yet.

- [ ] **Step 3: Add minimal dependencies and app factory**

Create `requirements.txt`:

```text
fastapi
uvicorn[standard]
sqlmodel
pytest
httpx
```

Create `app/__init__.py` as an empty file.

Create `app/database.py`:

```python
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///tanning_salon.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db(seed_database: bool = True) -> None:
    SQLModel.metadata.create_all(engine)
```

Create `app/main.py`:

```python
from fastapi import FastAPI

from app.database import init_db


def create_app(seed_database: bool = True) -> FastAPI:
    app = FastAPI(title="Tanning Salon API")

    @app.on_event("startup")
    def on_startup() -> None:
        init_db(seed_database=seed_database)

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **Step 4: Run the health-check test**

Run: `pytest tests/test_public_api.py::test_health_check_returns_ok -v`

Expected: PASS.

## Task 2: Models, Seed Data, And Public Catalog

**Files:**
- Create: `app/models.py`
- Create: `app/schemas.py`
- Create: `app/seed.py`
- Create: `app/routes_public.py`
- Modify: `app/database.py`
- Modify: `app/main.py`
- Modify: `tests/conftest.py`
- Modify: `tests/test_public_api.py`

- [ ] **Step 1: Write failing catalog tests**

Add tests to `tests/test_public_api.py`:

```python
def test_services_are_seeded(get_test_client):
    client = next(get_test_client)

    response = client.get("/services")

    assert response.status_code == 200
    names = {service["name"] for service in response.json()}
    assert names == {"UV Tanning", "Spray Tanning", "Teeth Whitening"}


def test_packages_can_be_filtered_by_service(get_test_client):
    client = next(get_test_client)

    services = client.get("/services").json()
    uv_service = next(service for service in services if service["name"] == "UV Tanning")
    response = client.get(f"/packages?service_id={uv_service['id']}")

    assert response.status_code == 200
    package_names = {package["name"] for package in response.json()}
    assert package_names == {
        "UV Tanning 5 Pack",
        "UV Tanning 10 Pack",
        "UV Tanning Monthly",
    }
```

- [ ] **Step 2: Run the catalog tests to verify they fail**

Run: `pytest tests/test_public_api.py::test_services_are_seeded tests/test_public_api.py::test_packages_can_be_filtered_by_service -v`

Expected: FAIL because `/services` and `/packages` do not exist.

- [ ] **Step 3: Implement models, schemas, seed data, and routes**

Implement enums and SQLModel tables in `app/models.py`:

```python
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class ServiceCategory(str, Enum):
    uv_tanning = "uv_tanning"
    spray_tanning = "spray_tanning"
    teeth_whitening = "teeth_whitening"


class PackageType(str, Enum):
    pack_5 = "pack_5"
    pack_10 = "pack_10"
    monthly = "monthly"
    single = "single"


class BookingSource(str, Enum):
    online = "online"
    walk_in = "walk_in"


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class Service(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    category: ServiceCategory
    duration_minutes: int
    description: str = ""
    is_active: bool = True


class Package(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    service_id: int = Field(foreign_key="service.id")
    name: str
    package_type: PackageType
    session_count: int | None = None
    valid_days: int | None = None
    price_cents: int
    description: str = ""
    is_active: bool = True


class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    phone: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Staff(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = ""
    phone: str = ""
    is_active: bool = True


class Appointment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    service_id: int = Field(foreign_key="service.id")
    package_id: int | None = Field(default=None, foreign_key="package.id")
    staff_id: int | None = Field(default=None, foreign_key="staff.id")
    appointment_time: datetime
    duration_minutes: int
    booking_source: BookingSource
    status: AppointmentStatus = AppointmentStatus.scheduled
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Purchase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    package_id: int = Field(foreign_key="package.id")
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    sessions_remaining: int | None = None
    is_active: bool = True
```

Create public response/request schemas in `app/schemas.py` with `SQLModel` base classes and separate create/update models for services, packages, clients, staff, appointments, and purchases.

Create `app/seed.py` with `seed_initial_data(session: Session) -> None`. It should insert exactly the services and packages from the design spec when there are no services yet.

Update `app/database.py` so `init_db()` calls `seed_initial_data()` when `seed_database=True`.

Create `app/routes_public.py` with:
- `GET /services`
- `GET /packages`

Update `app/main.py` to include the public router.

Update `tests/conftest.py` so the test client creates tables and calls `seed_initial_data(session)`.

- [ ] **Step 4: Run the catalog tests**

Run: `pytest tests/test_public_api.py::test_services_are_seeded tests/test_public_api.py::test_packages_can_be_filtered_by_service -v`

Expected: PASS.

## Task 3: Clients, Appointments, Availability, And Conflict Rules

**Files:**
- Modify: `app/schemas.py`
- Create: `app/services.py`
- Modify: `app/routes_public.py`
- Modify: `tests/test_public_api.py`

- [ ] **Step 1: Write failing client and booking tests**

Add tests for:
- `POST /clients` creates a client.
- `POST /appointments` creates an online appointment.
- `POST /appointments` creates a walk-in appointment.
- `POST /appointments` returns `409` for overlapping appointments assigned to the same staff member.
- `GET /appointments/availability` returns `{"available": false}` for a conflicting staff appointment.

- [ ] **Step 2: Run the booking tests to verify they fail**

Run: `pytest tests/test_public_api.py -v`

Expected: FAIL because client and appointment routes are missing.

- [ ] **Step 3: Implement booking business logic**

Create `app/services.py` functions:
- `get_or_404(session, model, record_id, label)`
- `ensure_package_matches_service(session, package_id, service_id)`
- `has_staff_conflict(session, staff_id, start_time, duration_minutes, exclude_appointment_id=None)`
- `create_appointment(session, appointment_in)`
- `check_availability(session, service_id, appointment_time, staff_id=None, duration_minutes=None)`

Conflict logic:
- Ignore appointments with status `cancelled`.
- Compare requested start/end with existing start/end.
- Conflict exists when `requested_start < existing_end and requested_end > existing_start`.
- Only enforce conflicts when `staff_id` is provided.

Update `app/routes_public.py` with:
- `POST /clients`
- `POST /appointments`
- `GET /appointments/availability`

- [ ] **Step 4: Run public API tests**

Run: `pytest tests/test_public_api.py -v`

Expected: PASS.

## Task 4: Admin CRUD

**Files:**
- Create: `app/routes_admin.py`
- Modify: `app/main.py`
- Create: `tests/test_admin_api.py`

- [ ] **Step 1: Write failing admin tests**

Create `tests/test_admin_api.py` covering:
- `POST /admin/services` creates a service.
- `PATCH /admin/services/{service_id}` updates a service.
- `DELETE /admin/services/{service_id}` deactivates a service.
- `POST /admin/packages` creates a package.
- `PATCH /admin/packages/{package_id}` updates a package.
- `DELETE /admin/packages/{package_id}` deactivates a package.
- `POST /admin/staff` creates staff.
- `GET /admin/appointments` lists appointments.

- [ ] **Step 2: Run admin tests to verify they fail**

Run: `pytest tests/test_admin_api.py -v`

Expected: FAIL because admin routes do not exist.

- [ ] **Step 3: Implement admin router**

Create `app/routes_admin.py` with an `APIRouter(prefix="/admin", tags=["admin"])`.

Implement list/get/create/patch/delete-or-deactivate for:
- services
- packages
- clients
- staff
- appointments
- purchases

Use deactivation for service, package, staff deletes by setting `is_active=False`.

Update `app/main.py` to include the admin router.

- [ ] **Step 4: Run admin tests**

Run: `pytest tests/test_admin_api.py -v`

Expected: PASS.

## Task 5: Purchases

**Files:**
- Modify: `app/services.py`
- Modify: `app/routes_admin.py`
- Create: `tests/test_purchases.py`

- [ ] **Step 1: Write failing purchase tests**

Create `tests/test_purchases.py` covering:
- Creating a 5-pack purchase sets `sessions_remaining` to `5`.
- Creating a monthly purchase sets `expires_at` based on `valid_days`.
- Creating a purchase for a missing client returns `404`.
- Creating a purchase for a missing package returns `404`.

- [ ] **Step 2: Run purchase tests to verify they fail**

Run: `pytest tests/test_purchases.py -v`

Expected: FAIL until purchase logic exists.

- [ ] **Step 3: Implement purchase logic**

Add `create_purchase(session, purchase_in)` to `app/services.py`.

Rules:
- Load client and package or return `404`.
- Set `sessions_remaining` to package `session_count`.
- If package `valid_days` is set, set `expires_at = purchase_date + timedelta(days=valid_days)`.
- Persist and return the purchase.

Use this function in `POST /admin/purchases`.

- [ ] **Step 4: Run purchase tests**

Run: `pytest tests/test_purchases.py -v`

Expected: PASS.

## Task 6: Final Verification And Documentation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README**

Document:
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `uvicorn app.main:app --reload`
- `pytest`
- example public and admin endpoints.

- [ ] **Step 2: Run all tests**

Run: `pytest -v`

Expected: all tests pass.

- [ ] **Step 3: Start the API locally**

Run: `uvicorn app.main:app --reload`

Expected: server starts and exposes docs at `http://127.0.0.1:8000/docs`.

- [ ] **Step 4: Stop the server after confirming startup**

Stop the uvicorn session with Ctrl-C.

