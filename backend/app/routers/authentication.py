from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import AuthSession, UserRecord
from ..core.security import hash_password, verify_password
from ..core.sessions import hash_token, issue_session, purge_expired
from ..dependencies import get_bearer_token

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = str(payload.email).lower()
    if db.scalar(select(UserRecord.id).where(UserRecord.email == email)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Вече има профил с този имейл."
        )
    user = UserRecord(
        email=email,
        name=payload.name,
        password_hash=hash_password(payload.password),
    )
    try:
        db.add(user)
        db.flush()
        token = issue_session(db, user.id)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Вече има профил с този имейл."
        ) from error
    return AuthResponse(access_token=token, user_id=str(user.id))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = str(payload.email).lower()
    user = db.scalar(select(UserRecord).where(UserRecord.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Грешен имейл или парола.")
    purge_expired(db)
    token = issue_session(db, user.id)
    db.commit()
    return AuthResponse(access_token=token, user_id=str(user.id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(get_bearer_token), db: Session = Depends(get_db)) -> Response:
    db.execute(delete(AuthSession).where(AuthSession.token_hash == hash_token(token)))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
