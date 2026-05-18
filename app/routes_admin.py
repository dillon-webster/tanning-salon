from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Appointment, Client, Package, Purchase, Service, Staff
from app.schemas import (AppointmentCreate, AppointmentRead, AppointmentUpdate,
                         ClientCreate, ClientRead, ClientUpdate, PackageCreate,
                         PackageRead, PackageUpdate, PurchaseCreate,
                         PurchaseRead, PurchaseUpdate, ServiceCreate,
                         ServiceRead, ServiceUpdate, StaffCreate, StaffRead,
                         StaffUpdate)
from app.security import require_admin_api_key
from app.services import create_appointment, create_purchase, get_or_404

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin_api_key)]
)


@router.get("/services", response_model=list[ServiceRead])
def list_admin_services(
    session: Annotated[Session, Depends(get_session)]
) -> list[Service]:
    return list(session.exec(select(Service)).all())


@router.get("/services/{service_id}", response_model=ServiceRead)
def get_admin_service(
    service_id: int, session: Annotated[Session, Depends(get_session)]
) -> Service:
    return get_or_404(session, Service, service_id, "Service")


@router.post(
    "/services", response_model=ServiceRead, status_code=status.HTTP_201_CREATED
)
def create_admin_service(
    service_in: ServiceCreate, session: Annotated[Session, Depends(get_session)]
) -> Service:
    service = Service.model_validate(service_in)
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


@router.patch("/services/{service_id}", response_model=ServiceRead)
def update_admin_service(
    service_id: int,
    service_in: ServiceUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> Service:
    service = get_or_404(session, Service, service_id, "Service")
    _apply_updates(service, service_in)
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


@router.delete("/services/{service_id}", response_model=ServiceRead)
def deactivate_admin_service(
    service_id: int, session: Annotated[Session, Depends(get_session)]
) -> Service:
    service = get_or_404(session, Service, service_id, "Service")
    service.is_active = False
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


@router.get("/packages", response_model=list[PackageRead])
def list_admin_packages(
    session: Annotated[Session, Depends(get_session)]
) -> list[Package]:
    return list(session.exec(select(Package)).all())


@router.get("/packages/{package_id}", response_model=PackageRead)
def get_admin_package(
    package_id: int, session: Annotated[Session, Depends(get_session)]
) -> Package:
    return get_or_404(session, Package, package_id, "Package")


@router.post(
    "/packages", response_model=PackageRead, status_code=status.HTTP_201_CREATED
)
def create_admin_package(
    package_in: PackageCreate, session: Annotated[Session, Depends(get_session)]
) -> Package:
    get_or_404(session, Service, package_in.service_id, "Service")
    package = Package.model_validate(package_in)
    session.add(package)
    session.commit()
    session.refresh(package)
    return package


@router.patch("/packages/{package_id}", response_model=PackageRead)
def update_admin_package(
    package_id: int,
    package_in: PackageUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> Package:
    package = get_or_404(session, Package, package_id, "Package")
    if package_in.service_id is not None:
        get_or_404(session, Service, package_in.service_id, "Service")
    _apply_updates(package, package_in)
    session.add(package)
    session.commit()
    session.refresh(package)
    return package


@router.delete("/packages/{package_id}", response_model=PackageRead)
def deactivate_admin_package(
    package_id: int, session: Annotated[Session, Depends(get_session)]
) -> Package:
    package = get_or_404(session, Package, package_id, "Package")
    package.is_active = False
    session.add(package)
    session.commit()
    session.refresh(package)
    return package


@router.get("/clients", response_model=list[ClientRead])
def list_admin_clients(
    session: Annotated[Session, Depends(get_session)]
) -> list[Client]:
    return list(session.exec(select(Client)).all())


@router.get("/clients/{client_id}", response_model=ClientRead)
def get_admin_client(
    client_id: int, session: Annotated[Session, Depends(get_session)]
) -> Client:
    return get_or_404(session, Client, client_id, "Client")


@router.post(
    "/clients", response_model=ClientRead, status_code=status.HTTP_201_CREATED
)
def create_admin_client(
    client_in: ClientCreate, session: Annotated[Session, Depends(get_session)]
) -> Client:
    client = Client.model_validate(client_in)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.patch("/clients/{client_id}", response_model=ClientRead)
def update_admin_client(
    client_id: int,
    client_in: ClientUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> Client:
    client = get_or_404(session, Client, client_id, "Client")
    _apply_updates(client, client_in)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.get("/staff", response_model=list[StaffRead])
def list_admin_staff(session: Annotated[Session, Depends(get_session)]) -> list[Staff]:
    return list(session.exec(select(Staff)).all())


@router.get("/staff/{staff_id}", response_model=StaffRead)
def get_admin_staff(
    staff_id: int, session: Annotated[Session, Depends(get_session)]
) -> Staff:
    return get_or_404(session, Staff, staff_id, "Staff")


@router.post("/staff", response_model=StaffRead, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_in: StaffCreate, session: Annotated[Session, Depends(get_session)]
) -> Staff:
    staff = Staff.model_validate(staff_in)
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff


@router.patch("/staff/{staff_id}", response_model=StaffRead)
def update_admin_staff(
    staff_id: int,
    staff_in: StaffUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> Staff:
    staff = get_or_404(session, Staff, staff_id, "Staff")
    _apply_updates(staff, staff_in)
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff


@router.delete("/staff/{staff_id}", response_model=StaffRead)
def deactivate_admin_staff(
    staff_id: int, session: Annotated[Session, Depends(get_session)]
) -> Staff:
    staff = get_or_404(session, Staff, staff_id, "Staff")
    staff.is_active = False
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff


@router.get("/appointments", response_model=list[AppointmentRead])
def list_admin_appointments(
    session: Annotated[Session, Depends(get_session)]
) -> list[Appointment]:
    return list(session.exec(select(Appointment)).all())


@router.get("/appointments/{appointment_id}", response_model=AppointmentRead)
def get_admin_appointment(
    appointment_id: int, session: Annotated[Session, Depends(get_session)]
) -> Appointment:
    return get_or_404(session, Appointment, appointment_id, "Appointment")


@router.post(
    "/appointments",
    response_model=AppointmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_admin_appointment(
    appointment_in: AppointmentCreate,
    session: Annotated[Session, Depends(get_session)],
) -> Appointment:
    return create_appointment(session, appointment_in)


@router.patch("/appointments/{appointment_id}", response_model=AppointmentRead)
def update_admin_appointment(
    appointment_id: int,
    appointment_in: AppointmentUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> Appointment:
    appointment = get_or_404(session, Appointment, appointment_id, "Appointment")
    _apply_updates(appointment, appointment_in)
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


@router.get("/purchases", response_model=list[PurchaseRead])
def list_admin_purchases(
    session: Annotated[Session, Depends(get_session)]
) -> list[Purchase]:
    return list(session.exec(select(Purchase)).all())


@router.get("/purchases/{purchase_id}", response_model=PurchaseRead)
def get_admin_purchase(
    purchase_id: int, session: Annotated[Session, Depends(get_session)]
) -> Purchase:
    return get_or_404(session, Purchase, purchase_id, "Purchase")


@router.post(
    "/purchases", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED
)
def create_admin_purchase(
    purchase_in: PurchaseCreate, session: Annotated[Session, Depends(get_session)]
) -> Purchase:
    return create_purchase(session, purchase_in)


@router.patch("/purchases/{purchase_id}", response_model=PurchaseRead)
def update_admin_purchase(
    purchase_id: int,
    purchase_in: PurchaseUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> Purchase:
    purchase = get_or_404(session, Purchase, purchase_id, "Purchase")
    _apply_updates(purchase, purchase_in)
    session.add(purchase)
    session.commit()
    session.refresh(purchase)
    return purchase


@router.delete("/purchases/{purchase_id}", response_model=PurchaseRead)
def deactivate_admin_purchase(
    purchase_id: int, session: Annotated[Session, Depends(get_session)]
) -> Purchase:
    purchase = get_or_404(session, Purchase, purchase_id, "Purchase")
    purchase.is_active = False
    session.add(purchase)
    session.commit()
    session.refresh(purchase)
    return purchase


def _apply_updates(model, update_model) -> None:
    for field, value in update_model.model_dump(exclude_unset=True).items():
        setattr(model, field, value)
