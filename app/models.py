from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from app.time import utc_now


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
    created_at: datetime = Field(default_factory=utc_now)


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
    created_at: datetime = Field(default_factory=utc_now)


class Purchase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    package_id: int = Field(foreign_key="package.id")
    purchase_date: datetime = Field(default_factory=utc_now)
    expires_at: datetime | None = None
    sessions_remaining: int | None = None
    is_active: bool = True
