from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Client, Package, Service
from app.schemas import (AppointmentCreate, AppointmentRead, AvailabilityRead,
                         ClientCreate, ClientRead, PackageRead, ServiceRead)
from app.services import check_availability, create_appointment

router = APIRouter(tags=["public"])


@router.get("/services", response_model=list[ServiceRead])
def list_services(session: Annotated[Session, Depends(get_session)]) -> list[Service]:
    statement = select(Service).where(Service.is_active == True)  # noqa: E712
    return list(session.exec(statement).all())


@router.get("/packages", response_model=list[PackageRead])
def list_packages(
    session: Annotated[Session, Depends(get_session)],
    service_id: int | None = None,
) -> list[Package]:
    statement = select(Package).where(Package.is_active == True)  # noqa: E712
    if service_id is not None:
        statement = statement.where(Package.service_id == service_id)
    return list(session.exec(statement).all())


@router.post("/clients", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate, session: Annotated[Session, Depends(get_session)]
) -> Client:
    client = Client.model_validate(client_in)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.post(
    "/appointments",
    response_model=AppointmentRead,
    status_code=status.HTTP_201_CREATED,
)
def book_appointment(
    appointment_in: AppointmentCreate,
    session: Annotated[Session, Depends(get_session)],
):
    return create_appointment(session, appointment_in)


@router.get("/appointments/availability", response_model=AvailabilityRead)
def get_appointment_availability(
    session: Annotated[Session, Depends(get_session)],
    service_id: int,
    appointment_time: datetime,
    staff_id: int | None = None,
    duration_minutes: int | None = None,
) -> AvailabilityRead:
    available = check_availability(
        session=session,
        service_id=service_id,
        appointment_time=appointment_time,
        staff_id=staff_id,
        duration_minutes=duration_minutes,
    )
    return AvailabilityRead(available=available)

@router.get("/hello")
def hello(session: Annotated[Session, Depends(get_session)]):
    statement = select(Service).where(Service.is_active == True)  # noqa: E712
    return list(session.exec(statement).all())
    #return "Hello World!"
