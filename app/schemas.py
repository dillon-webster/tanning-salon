from datetime import datetime

from sqlmodel import SQLModel

from app.models import (AppointmentStatus, BookingSource, PackageType,
                        ServiceCategory)


class ServiceBase(SQLModel):
    name: str
    category: ServiceCategory
    duration_minutes: int
    description: str = ""
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int


class ServiceUpdate(SQLModel):
    name: str | None = None
    category: ServiceCategory | None = None
    duration_minutes: int | None = None
    description: str | None = None
    is_active: bool | None = None


class PackageBase(SQLModel):
    service_id: int
    name: str
    package_type: PackageType
    session_count: int | None = None
    valid_days: int | None = None
    price_cents: int
    description: str = ""
    is_active: bool = True


class PackageCreate(PackageBase):
    pass


class PackageRead(PackageBase):
    id: int


class PackageUpdate(SQLModel):
    service_id: int | None = None
    name: str | None = None
    package_type: PackageType | None = None
    session_count: int | None = None
    valid_days: int | None = None
    price_cents: int | None = None
    description: str | None = None
    is_active: bool | None = None


class ClientBase(SQLModel):
    first_name: str
    last_name: str
    email: str
    phone: str


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: int
    created_at: datetime


class ClientUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None


class StaffBase(SQLModel):
    name: str
    email: str = ""
    phone: str = ""
    is_active: bool = True


class StaffCreate(StaffBase):
    pass


class StaffRead(StaffBase):
    id: int


class StaffUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class AppointmentCreate(SQLModel):
    client_id: int
    service_id: int
    package_id: int | None = None
    staff_id: int | None = None
    appointment_time: datetime
    duration_minutes: int | None = None
    booking_source: BookingSource = BookingSource.online
    notes: str = ""


class AppointmentRead(SQLModel):
    id: int
    client_id: int
    service_id: int
    package_id: int | None
    staff_id: int | None
    appointment_time: datetime
    duration_minutes: int
    booking_source: BookingSource
    status: AppointmentStatus
    notes: str
    created_at: datetime


class AppointmentUpdate(SQLModel):
    client_id: int | None = None
    service_id: int | None = None
    package_id: int | None = None
    staff_id: int | None = None
    appointment_time: datetime | None = None
    duration_minutes: int | None = None
    booking_source: BookingSource | None = None
    status: AppointmentStatus | None = None
    notes: str | None = None


class AvailabilityRead(SQLModel):
    available: bool


class PurchaseCreate(SQLModel):
    client_id: int
    package_id: int
    purchase_date: datetime | None = None


class PurchaseRead(SQLModel):
    id: int
    client_id: int
    package_id: int
    purchase_date: datetime
    expires_at: datetime | None
    sessions_remaining: int | None
    is_active: bool


class PurchaseUpdate(SQLModel):
    expires_at: datetime | None = None
    sessions_remaining: int | None = None
    is_active: bool | None = None
