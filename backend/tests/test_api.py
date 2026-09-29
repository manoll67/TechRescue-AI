from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import AuthSession, UserRecord

CREDENTIALS = {"email": "ana@example.com", "name": "Ана", "password": "parola1234"}


def register(client: TestClient, **overrides) -> str:
    payload = {**CREDENTIALS, **overrides}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_register_normalizes_email_and_rejects_duplicates(client: TestClient) -> None:
    register(client, email="Ana@Example.com")
    duplicate = client.post("/api/v1/auth/register", json=CREDENTIALS)
    assert duplicate.status_code == 409
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ANA@EXAMPLE.COM", "password": CREDENTIALS["password"]},
    )
    assert login.status_code == 200


def test_login_rejects_wrong_password(client: TestClient) -> None:
    register(client)
    response = client.post(
        "/api/v1/auth/login", json={"email": CREDENTIALS["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_protected_routes_require_a_valid_token(client: TestClient) -> None:
    assert client.get("/api/v1/users/me").status_code == 401
    assert client.get("/api/v1/users/me", headers=auth("nonsense")).status_code == 401


def test_logout_revokes_the_token(client: TestClient) -> None:
    token = register(client)
    assert client.post("/api/v1/auth/logout", headers=auth(token)).status_code == 204
    assert client.get("/api/v1/users/me", headers=auth(token)).status_code == 401


def test_expired_session_is_rejected_and_removed(
    client: TestClient, db_session: Session
) -> None:
    token = register(client)
    session = db_session.scalars(select(AuthSession)).one()
    session.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    assert client.get("/api/v1/users/me", headers=auth(token)).status_code == 401
    assert db_session.scalars(select(AuthSession)).all() == []


def test_chat_persists_conversation_and_isolates_users(client: TestClient) -> None:
    token = register(client)
    first = client.post(
        "/api/v1/chat/messages", json={"message": "бавен компютър"}, headers=auth(token)
    )
    assert first.status_code == 200
    conversation_id = first.json()["conversation_id"]

    followup = client.post(
        "/api/v1/chat/messages",
        json={"message": "още детайли", "conversation_id": conversation_id},
        headers=auth(token),
    )
    assert followup.status_code == 200

    other = register(client, email="boris@example.com")
    stolen = client.post(
        "/api/v1/chat/messages",
        json={"message": "чужд разговор", "conversation_id": conversation_id},
        headers=auth(other),
    )
    assert stolen.status_code == 404


def test_tickets_are_persisted_per_user(client: TestClient) -> None:
    token = register(client)
    created = client.post(
        "/api/v1/tickets",
        json={"subject": "Син екран", "description": "При стартиране."},
        headers=auth(token),
    )
    assert created.status_code == 201
    assert created.json()["status"] == "open"

    mine = client.get("/api/v1/tickets", headers=auth(token))
    assert [ticket["subject"] for ticket in mine.json()] == ["Син екран"]

    other = register(client, email="boris@example.com")
    assert client.get("/api/v1/tickets", headers=auth(other)).json() == []


def test_knowledge_base_is_public_to_read_and_admin_only_to_write(
    client: TestClient, db_session: Session
) -> None:
    token = register(client)
    article = {"title": "Как да рестартираш", "content": "Стъпки", "category": "windows"}

    assert client.post("/api/v1/knowledge-base", json=article).status_code == 401
    assert client.post("/api/v1/knowledge-base", json=article, headers=auth(token)).status_code == 403

    user = db_session.scalars(select(UserRecord)).one()
    user.role = "admin"
    db_session.commit()

    created = client.post("/api/v1/knowledge-base", json=article, headers=auth(token))
    assert created.status_code == 201
    assert [item["title"] for item in client.get("/api/v1/knowledge-base").json()] == [
        article["title"]
    ]


def test_admin_stats_require_admin_role(client: TestClient) -> None:
    token = register(client)
    assert client.get("/api/v1/admin/stats", headers=auth(token)).status_code == 403
