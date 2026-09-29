from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import Ticket, UserRecord
from ..dependencies import get_current_user

router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=1, max_length=10000)


class TicketResponse(BaseModel):
    id: str
    user_id: str
    subject: str
    description: str
    status: str
    created_at: datetime


def serialize(ticket: Ticket) -> TicketResponse:
    return TicketResponse(
        id=str(ticket.id),
        user_id=str(ticket.user_id),
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status,
        created_at=ticket.created_at,
    )


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TicketResponse:
    ticket = Ticket(user_id=user.id, subject=payload.subject, description=payload.description)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return serialize(ticket)


@router.get("", response_model=list[TicketResponse])
def list_tickets(
    user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TicketResponse]:
    tickets = db.scalars(
        select(Ticket).where(Ticket.user_id == user.id).order_by(Ticket.created_at.desc())
    ).all()
    return [serialize(ticket) for ticket in tickets]
