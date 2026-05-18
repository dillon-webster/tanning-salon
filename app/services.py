from datetime import datetime, timedelta
from typing import TypeVar

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, select

from app.models import (
    Appointment,
    AppointmentStatus,
    Client,
    Package,
    Purchase,
    Service,
    Staff,
)
from app.schemas import AppointmentCreate, PurchaseCreate
from app.time import utc_now

ModelT = TypeVar("ModelT", bound=SQLModel)


def get_or_404(session: Session, model: type[ModelT], record_id: int, label: str) -> ModelT:
    record = session.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{label} not found.")
    return record


def ensure_package_matches_service(
    session: Session, package_id: int | None, service_id: int
) -> None:
    if package_id is None:
        return
    package = get_or_404(session, Package, package_id, "Package")
    if package.service_id != service_id:
        raise HTTPException(status_code=400, detail="Package does not match service.")


def has_staff_conflict(
    session: Session,
    staff_id: int | None,
    start_time: datetime,
    duration_minutes: int,
    exclude_appointment_id: int | None = None,
) -> bool:
    if staff_id is None:
        return False

    requested_end = start_time + timedelta(minutes=duration_minutes)
    statement = select(Appointment).where(
        Appointment.staff_id == staff_id,
        Appointment.status != AppointmentStatus.cancelled,
    )
    if exclude_appointment_id is not None:
        statement = statement.where(Appointment.id != exclude_appointment_id)

    for appointment in session.exec(statement).all():
        existing_start = appointment.appointment_time
        existing_end = existing_start + timedelta(minutes=appointment.duration_minutes)
        if start_time < existing_end and requested_end > existing_start:
            return True
    return False


def create_appointment(
    session: Session, appointment_in: AppointmentCreate
) -> Appointment:
    client = get_or_404(session, Client, appointment_in.client_id, "Client")
    service = get_or_404(session, Service, appointment_in.service_id, "Service")
    if appointment_in.staff_id is not None:
        get_or_404(session, Staff, appointment_in.staff_id, "Staff")
    ensure_package_matches_service(
        session, appointment_in.package_id, appointment_in.service_id
    )

    duration_minutes = appointment_in.duration_minutes or service.duration_minutes
    if has_staff_conflict(
        session,
        appointment_in.staff_id,
        appointment_in.appointment_time,
        duration_minutes,
    ):
        raise HTTPException(
            status_code=409, detail="Appointment time is not available."
        )

    appointment = Appointment(
        client_id=client.id,
        service_id=service.id,
        package_id=appointment_in.package_id,
        staff_id=appointment_in.staff_id,
        appointment_time=appointment_in.appointment_time,
        duration_minutes=duration_minutes,
        booking_source=appointment_in.booking_source,
        notes=appointment_in.notes,
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def check_availability(
    session: Session,
    service_id: int,
    appointment_time: datetime,
    staff_id: int | None = None,
    duration_minutes: int | None = None,
) -> bool:
    service = get_or_404(session, Service, service_id, "Service")
    duration = duration_minutes or service.duration_minutes
    if staff_id is not None:
        get_or_404(session, Staff, staff_id, "Staff")
    return not has_staff_conflict(session, staff_id, appointment_time, duration)


def create_purchase(session: Session, purchase_in: PurchaseCreate) -> Purchase:
    package = get_or_404(session, Package, purchase_in.package_id, "Package")
    client = get_or_404(session, Client, purchase_in.client_id, "Client")
    purchase_date = purchase_in.purchase_date or utc_now()
    expires_at = None
    if package.valid_days is not None:
        expires_at = purchase_date + timedelta(days=package.valid_days)

    purchase = Purchase(
        client_id=client.id,
        package_id=package.id,
        purchase_date=purchase_date,
        expires_at=expires_at,
        sessions_remaining=package.session_count,
    )
    session.add(purchase)
    session.commit()
    session.refresh(purchase)
    return purchase
