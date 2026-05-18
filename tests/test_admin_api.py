def test_admin_rejects_missing_api_key(client):
    response = client.get("/admin/services")

    assert response.status_code == 401
    assert response.json()["detail"] == "Admin API key is required."


def test_admin_rejects_invalid_api_key(client):
    response = client.get(
        "/admin/services", headers={"X-Admin-API-Key": "wrong-key"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid admin API key."


def test_admin_creates_updates_and_deactivates_service(client, admin_headers):
    create_response = client.post(
        "/admin/services",
        json={
            "name": "Red Light Therapy",
            "category": "uv_tanning",
            "duration_minutes": 15,
            "description": "Optional add-on session.",
            "is_active": True,
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201
    service_id = create_response.json()["id"]

    update_response = client.patch(
        f"/admin/services/{service_id}",
        json={"duration_minutes": 25, "description": "Updated description."},
        headers=admin_headers,
    )
    delete_response = client.delete(
        f"/admin/services/{service_id}", headers=admin_headers
    )

    assert update_response.status_code == 200
    assert update_response.json()["duration_minutes"] == 25
    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False


def test_admin_creates_updates_and_deactivates_package(client, admin_headers):
    service = _service_named(client, "UV Tanning")
    create_response = client.post(
        "/admin/packages",
        json={
            "service_id": service["id"],
            "name": "UV Trial Session",
            "package_type": "single",
            "session_count": 1,
            "valid_days": 30,
            "price_cents": 1500,
            "description": "Trial package.",
            "is_active": True,
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201
    package_id = create_response.json()["id"]

    update_response = client.patch(
        f"/admin/packages/{package_id}",
        json={"price_cents": 1800, "name": "UV Starter Session"},
        headers=admin_headers,
    )
    delete_response = client.delete(
        f"/admin/packages/{package_id}", headers=admin_headers
    )

    assert update_response.status_code == 200
    assert update_response.json()["price_cents"] == 1800
    assert update_response.json()["name"] == "UV Starter Session"
    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False


def test_admin_creates_staff(client, admin_headers):
    response = client.post(
        "/admin/staff",
        json={"name": "Jordan Lee", "email": "jordan@example.com", "phone": "555-0101"},
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Jordan Lee"


def test_admin_lists_appointments(client, admin_headers):
    created_client = _create_client(client)
    service = _service_named(client, "Spray Tanning")
    client.post(
        "/appointments",
        json={
            "client_id": created_client["id"],
            "service_id": service["id"],
            "appointment_time": "2026-05-07T14:00:00",
            "booking_source": "online",
        },
    )

    response = client.get("/admin/appointments", headers=admin_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_admin_lists_and_gets_clients(client, admin_headers):
    created_client = _create_client(client)

    list_response = client.get("/admin/clients", headers=admin_headers)
    get_response = client.get(
        f"/admin/clients/{created_client['id']}", headers=admin_headers
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert get_response.status_code == 200
    assert get_response.json()["email"] == created_client["email"]


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
