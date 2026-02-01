import uuid
from fastapi.testclient import TestClient
from main import app, SessionLocal, User

client = TestClient(app)


def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "Identity Verification API is running" in r.json().get("message", "")


def test_register_login_verify_and_admin_denied():
    email = unique_email()

    # register
    r = client.post("/register", json={"email": email, "password": "secret"})
    assert r.status_code == 200

    # duplicate registration should fail
    r = client.post("/register", json={"email": email, "password": "secret"})
    assert r.status_code == 400

    # login
    r = client.post("/login", data={"username": email, "password": "secret"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # me
    r = client.get("/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == email

    # verify id (even last digit -> verified)
    r = client.post(
        "/verify-id",
        json={"id_type": "NIA", "id_number": "12345678"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "verified"

    # listing admin verifications should fail for non-admin
    r = client.get("/admin/verifications", headers=headers)
    assert r.status_code == 403


def test_admin_can_list_verifications():
    email = unique_email()

    # register and login
    r = client.post("/register", json={"email": email, "password": "secret"})
    assert r.status_code == 200
    r = client.post("/login", data={"username": email, "password": "secret"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create a verification
    r = client.post(
        "/verify-id",
        json={"id_type": "NHIS", "id_number": "87654321"},
        headers=headers,
    )
    assert r.status_code == 200

    # promote user to admin in DB
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.is_admin = True
    db.commit()
    db.close()

    # now admin endpoint should return data
    r = client.get("/admin/verifications", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)