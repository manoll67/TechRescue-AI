from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import UserRecord
from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str


class UserUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


def serialize(user: UserRecord) -> UserResponse:
    return UserResponse(id=str(user.id), email=user.email, name=user.name, role=user.role)


@router.get("/me", response_model=UserResponse)
def get_me(user: UserRecord = Depends(get_current_user)) -> UserResponse:
    return serialize(user)


@router.patch("/me", response_model=UserResponse)
def update_me(
    payload: UserUpdate,
    user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    user.name = payload.name
    db.commit()
    db.refresh(user)
    return serialize(user)
