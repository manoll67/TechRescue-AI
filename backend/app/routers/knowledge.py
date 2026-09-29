from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.models import Article, UserRecord
from ..dependencies import require_admin

router = APIRouter(prefix="/knowledge-base", tags=["knowledge base"])


class ArticleCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=1, max_length=20000)
    category: str = Field(min_length=2, max_length=80)


class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    created_at: datetime


def serialize(article: Article) -> ArticleResponse:
    return ArticleResponse(
        id=str(article.id),
        title=article.title,
        content=article.content,
        category=article.category,
        created_at=article.created_at,
    )


@router.get("", response_model=list[ArticleResponse])
def list_articles(
    db: Session = Depends(get_db),
    category: str | None = Query(default=None, max_length=80),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ArticleResponse]:
    query = select(Article).order_by(Article.created_at.desc()).limit(limit).offset(offset)
    if category is not None:
        query = query.where(Article.category == category)
    articles = db.scalars(query).all()
    return [serialize(article) for article in articles]


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    payload: ArticleCreate,
    _: UserRecord = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ArticleResponse:
    article = Article(title=payload.title, content=payload.content, category=payload.category)
    db.add(article)
    db.commit()
    db.refresh(article)
    return serialize(article)
