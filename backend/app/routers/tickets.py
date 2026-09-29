from uuid import uuid4

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from ..dependencies import get_current_user
from ..core.models import UserRecord
from ..core.store import tickets

router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=1, max_length=10000)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, user: UserRecord = Depends(get_current_user)) -> dict:
    ticket = {"id": str(uuid4()), "user_id": str(user.id), "status": "open", **payload.model_dump()}
    tickets.append(ticket)
    return ticket


@router.get("")
def list_tickets(user: UserRecord = Depends(get_current_user)) -> list[dict]:
    return [ticket for ticket in tickets if ticket["user_id"] == str(user.id)]
