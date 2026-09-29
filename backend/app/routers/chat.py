from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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
    db.add_all(
        [
            Message(conversation_id=conversation.id, role="user", content=payload.message),
            Message(conversation_id=conversation.id, role="assistant", content=answer),
        ]
    )
    db.commit()
    return ChatResponse(conversation_id=str(conversation.id), answer=answer)
