from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..dependencies import require_admin
from ..core.database import get_db
from ..core.models import UserRecord

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    _: UserRecord = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    return {"users": db.scalar(select(func.count()).select_from(UserRecord)) or 0}
