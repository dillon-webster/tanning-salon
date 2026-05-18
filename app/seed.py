from sqlmodel import Session, select

from app.models import Package, PackageType, Service, ServiceCategory


def seed_initial_data(session: Session) -> None:
    existing_service = session.exec(select(Service)).first()
    if existing_service:
        return

    services = [
        Service(
            name="UV Tanning",
            category=ServiceCategory.uv_tanning,
            duration_minutes=20,
            description="Traditional UV tanning session.",
        ),
        Service(
            name="Spray Tanning",
            category=ServiceCategory.spray_tanning,
            duration_minutes=30,
            description="Sunless spray tanning session.",
        ),
        Service(
            name="Teeth Whitening",
            category=ServiceCategory.teeth_whitening,
            duration_minutes=45,
            description="Cosmetic teeth whitening session.",
        ),
    ]
    session.add_all(services)
    session.commit()

    uv_tanning, spray_tanning, teeth_whitening = services
    packages = [
        Package(
            service_id=uv_tanning.id,
            name="UV Tanning 5 Pack",
            package_type=PackageType.pack_5,
            session_count=5,
            price_cents=4500,
        ),
        Package(
            service_id=uv_tanning.id,
            name="UV Tanning 10 Pack",
            package_type=PackageType.pack_10,
            session_count=10,
            price_cents=8000,
        ),
        Package(
            service_id=uv_tanning.id,
            name="UV Tanning Monthly",
            package_type=PackageType.monthly,
            valid_days=30,
            price_cents=5900,
        ),
        Package(
            service_id=spray_tanning.id,
            name="Spray Tanning 5 Pack",
            package_type=PackageType.pack_5,
            session_count=5,
            price_cents=12000,
        ),
        Package(
            service_id=spray_tanning.id,
            name="Spray Tanning 10 Pack",
            package_type=PackageType.pack_10,
            session_count=10,
            price_cents=22000,
        ),
        Package(
            service_id=spray_tanning.id,
            name="Spray Tanning Monthly",
            package_type=PackageType.monthly,
            valid_days=30,
            price_cents=14900,
        ),
        Package(
            service_id=teeth_whitening.id,
            name="Teeth Whitening Single Session",
            package_type=PackageType.single,
            session_count=1,
            price_cents=7900,
        ),
        Package(
            service_id=teeth_whitening.id,
            name="Teeth Whitening 5 Pack",
            package_type=PackageType.pack_5,
            session_count=5,
            price_cents=35000,
        ),
    ]
    session.add_all(packages)
    session.commit()
