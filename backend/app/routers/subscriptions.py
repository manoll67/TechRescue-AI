from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..core.models import UserRecord
from ..dependencies import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class SubscriptionResponse(BaseModel):
    plan: str
    status: str


@router.get("/me", response_model=SubscriptionResponse)
def get_subscription(user: UserRecord = Depends(get_current_user)) -> SubscriptionResponse:
    return SubscriptionResponse(plan=user.subscription, status="active")
