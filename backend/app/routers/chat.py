from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import Conversation, Message, UserRecord
from ..dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


@router.post("/messages", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    if payload.conversation_id is None:
        conversation = Conversation(user_id=user.id, title=payload.message[:200])
        db.add(conversation)
        db.flush()
    else:
        conversation = db.scalar(
            select(Conversation).where(
                Conversation.id == payload.conversation_id,
                Conversation.user_id == user.id,
            )
        )
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Разговорът не е намерен.")

    answer = "Получих въпроса ти. Следващата стъпка е да уточним операционната система и точния текст на грешката."
    asked_at = datetime.now(timezone.utc)
    db.add_all(
        [
            Message(
                conversation_id=conversation.id,
                role="user",
                content=payload.message,
                created_at=asked_at,
            ),
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                created_at=asked_at + timedelta(milliseconds=1),
            ),
        ]
    )
    db.commit()
    return ChatResponse(conversation_id=str(conversation.id), answer=answer)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ConversationResponse]:
    conversations = db.scalars(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [
        ConversationResponse(
            id=str(conversation.id), title=conversation.title, created_at=conversation.created_at
        )
        for conversation in conversations
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(
    conversation_id: UUID,
    user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[MessageResponse]:
    owns_conversation = db.scalar(
        select(Conversation.id).where(
            Conversation.id == conversation_id, Conversation.user_id == user.id
        )
    )
    if owns_conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Разговорът не е намерен.")

    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
        .limit(limit)
        .offset(offset)
    ).all()
    return [
        MessageResponse(
            id=str(message.id),
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        for message in messages
    ]
