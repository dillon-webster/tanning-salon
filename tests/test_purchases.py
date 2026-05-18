def test_creating_five_pack_purchase_sets_sessions_remaining(client, admin_headers):
    created_client = _create_client(client)
    package = _package_named(client, "UV Tanning 5 Pack")

    response = client.post(
        "/admin/purchases",
        json={"client_id": created_client["id"], "package_id": package["id"]},
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["sessions_remaining"] == 5
    assert response.json()["expires_at"] is None


def test_creating_monthly_purchase_sets_expiration(client, admin_headers):
    created_client = _create_client(client)
    package = _package_named(client, "UV Tanning Monthly")

    response = client.post(
        "/admin/purchases",
        json={
            "client_id": created_client["id"],
            "package_id": package["id"],
            "purchase_date": "2026-05-07T09:00:00",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["sessions_remaining"] is None
    assert response.json()["expires_at"] == "2026-06-06T09:00:00"


def test_creating_purchase_for_missing_client_returns_404(client, admin_headers):
    package = _package_named(client, "UV Tanning 5 Pack")

    response = client.post(
        "/admin/purchases",
        json={"client_id": 999, "package_id": package["id"]},
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found."


def test_creating_purchase_for_missing_package_returns_404(client, admin_headers):
    created_client = _create_client(client)

    response = client.post(
        "/admin/purchases",
        json={"client_id": created_client["id"], "package_id": 999},
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Package not found."


def test_admin_deactivates_purchase(client, admin_headers):
    created_client = _create_client(client)
    package = _package_named(client, "Teeth Whitening 5 Pack")
    purchase = client.post(
        "/admin/purchases",
        json={"client_id": created_client["id"], "package_id": package["id"]},
        headers=admin_headers,
    ).json()

    response = client.delete(
        f"/admin/purchases/{purchase['id']}", headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


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


def _package_named(client, name):
    packages = client.get("/packages").json()
    return next(package for package in packages if package["name"] == name)
