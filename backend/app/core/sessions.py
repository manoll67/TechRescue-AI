import hashlib
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from sqlalchemy import delete
from sqlalchemy.orm import Session

from .config import get_settings
from .models import AuthSession


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_session(db: Session, user_id) -> str:
    token = token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=get_settings().session_ttl_hours)
    db.add(AuthSession(token_hash=hash_token(token), user_id=user_id, expires_at=expires_at))
    return token


def purge_expired(db: Session) -> None:
    db.execute(delete(AuthSession).where(AuthSession.expires_at <= datetime.now(timezone.utc)))
