from uuid import uuid4

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from ..dependencies import require_admin
from ..core.models import UserRecord
from ..core.store import knowledge_articles

router = APIRouter(prefix="/knowledge-base", tags=["knowledge base"])


class ArticleCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=1, max_length=20000)
    category: str = Field(min_length=2, max_length=80)


@router.get("")
def list_articles() -> list[dict]:
    return knowledge_articles


@router.post("", status_code=status.HTTP_201_CREATED)
def create_article(payload: ArticleCreate, _: UserRecord = Depends(require_admin)) -> dict:
    article = {"id": str(uuid4()), **payload.model_dump()}
    knowledge_articles.append(article)
    return article
