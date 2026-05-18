def test_health_check_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_services_are_seeded(client):
    response = client.get("/services")

    assert response.status_code == 200
    names = {service["name"] for service in response.json()}
    assert names == {"UV Tanning", "Spray Tanning", "Teeth Whitening"}


def test_packages_can_be_filtered_by_service(client):
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


def test_create_client(client):
    response = client.post(
        "/clients",
        json={
            "first_name": "Avery",
            "last_name": "Stone",
            "email": "avery@example.com",
            "phone": "555-0100",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["email"] == "avery@example.com"


def test_create_online_appointment(client):
    created_client = _create_client(client)
    service = _service_named(client, "UV Tanning")

    response = client.post(
        "/appointments",
        json={
            "client_id": created_client["id"],
            "service_id": service["id"],
            "appointment_time": "2026-05-07T10:00:00",
            "booking_source": "online",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["client_id"] == created_client["id"]
    assert data["service_id"] == service["id"]
    assert data["duration_minutes"] == service["duration_minutes"]
    assert data["booking_source"] == "online"
    assert data["status"] == "scheduled"


def test_create_walk_in_appointment(client):
    created_client = _create_client(client)
    service = _service_named(client, "Spray Tanning")

    response = client.post(
        "/appointments",
        json={
            "client_id": created_client["id"],
            "service_id": service["id"],
            "appointment_time": "2026-05-07T11:00:00",
            "booking_source": "walk_in",
            "notes": "Came in without booking.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["booking_source"] == "walk_in"
    assert data["notes"] == "Came in without booking."


def test_staff_appointment_conflict_returns_409(client, admin_headers):
    created_client = _create_client(client)
    service = _service_named(client, "UV Tanning")
    staff = _create_staff(client, admin_headers)
    appointment_payload = {
        "client_id": created_client["id"],
        "service_id": service["id"],
        "staff_id": staff["id"],
        "appointment_time": "2026-05-07T12:00:00",
        "duration_minutes": 30,
        "booking_source": "online",
    }
    first_response = client.post("/appointments", json=appointment_payload)

    conflict_response = client.post(
        "/appointments",
        json={
            **appointment_payload,
            "appointment_time": "2026-05-07T12:15:00",
        },
    )

    assert first_response.status_code == 201
    assert conflict_response.status_code == 409
    assert conflict_response.json()["detail"] == "Appointment time is not available."


def test_availability_returns_false_for_staff_conflict(client, admin_headers):
    created_client = _create_client(client)
    service = _service_named(client, "UV Tanning")
    staff = _create_staff(client, admin_headers)
    client.post(
        "/appointments",
        json={
            "client_id": created_client["id"],
            "service_id": service["id"],
            "staff_id": staff["id"],
            "appointment_time": "2026-05-07T13:00:00",
            "duration_minutes": 30,
            "booking_source": "online",
        },
    )

    response = client.get(
        "/appointments/availability",
        params={
            "service_id": service["id"],
            "staff_id": staff["id"],
            "appointment_time": "2026-05-07T13:15:00",
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"available": False}


def _create_client(client):
    response = client.post(
        "/clients",
        json={
            "first_name": "Avery",
            "last_name": "Stone",
            "email": "avery@example.com",
            "phone": "555-0100",
        },
    )
    return response.json()


def _service_named(client, name):
    services = client.get("/services").json()
    return next(service for service in services if service["name"] == name)


def _create_staff(client, admin_headers):
    response = client.post(
        "/admin/staff",
        json={"name": "Jordan Lee", "email": "jordan@example.com", "phone": "555-0101"},
        headers=admin_headers,
    )
    return response.json()
