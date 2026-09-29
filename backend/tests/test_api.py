from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.models import AuthSession, UserRecord

CREDENTIALS = {"email": "ana@example.com", "name": "Ана", "password": "parola1234"}
LOGIN_LIMIT = get_settings().login_attempt_limit


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
    assert duplicate.json()["detail"] == "Вече има профил с този имейл."
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
    assert response.json()["detail"] == "Грешен имейл или парола."


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


def test_admin_stats_count_users_for_admins(client: TestClient, db_session: Session) -> None:
    token = register(client)
    user = db_session.scalars(select(UserRecord)).one()
    user.role = "admin"
    db_session.commit()

    response = client.get("/api/v1/admin/stats", headers=auth(token))
    assert response.status_code == 200
    assert response.json() == {"users": 1}


def test_repeated_login_attempts_are_rate_limited(client: TestClient) -> None:
    register(client)
    attempt = {"email": CREDENTIALS["email"], "password": "wrongpassword"}
    statuses = {
        client.post("/api/v1/auth/login", json=attempt).status_code for _ in range(LOGIN_LIMIT + 2)
    }
    assert statuses == {401, 429}


def test_unauthorized_responses_advertise_the_bearer_scheme(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_conversation_history_is_readable_only_by_its_owner(client: TestClient) -> None:
    token = register(client)
    conversation_id = client.post(
        "/api/v1/chat/messages", json={"message": "бавен компютър"}, headers=auth(token)
    ).json()["conversation_id"]

    conversations = client.get("/api/v1/chat/conversations", headers=auth(token))
    assert [item["id"] for item in conversations.json()] == [conversation_id]

    messages = client.get(
        f"/api/v1/chat/conversations/{conversation_id}/messages", headers=auth(token)
    )
    assert [(item["role"], item["content"]) for item in messages.json()] == [
        ("user", "бавен компютър"),
        ("assistant", messages.json()[1]["content"]),
    ]

    other = register(client, email="boris@example.com")
    assert client.get("/api/v1/chat/conversations", headers=auth(other)).json() == []
    assert (
        client.get(
            f"/api/v1/chat/conversations/{conversation_id}/messages", headers=auth(other)
        ).status_code
        == 404
    )


def test_profile_can_be_renamed(client: TestClient) -> None:
    token = register(client)
    response = client.patch("/api/v1/users/me", json={"name": "Ана Петрова"}, headers=auth(token))
    assert response.status_code == 200
    assert response.json()["name"] == "Ана Петрова"
    assert response.json()["subscription"] == "free"


def test_subscription_and_diagnosis_require_a_session(client: TestClient) -> None:
    assert client.get("/api/v1/subscriptions/me").status_code == 401
    token = register(client)
    assert client.get("/api/v1/subscriptions/me", headers=auth(token)).json() == {
        "plan": "free",
        "status": "active",
    }
    diagnosis = client.post(
        "/api/v1/ai/diagnose",
        json={"problem": "Компютърът замръзва.", "operating_system": "Windows"},
        headers=auth(token),
    )
    assert diagnosis.status_code == 200
    assert diagnosis.json()["steps"]


def test_cors_origins_accept_a_comma_separated_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TECHRESCUE_CORS_ORIGINS", "https://a.example, https://b.example")
    assert Settings().cors_origins == ["https://a.example", "https://b.example"]
