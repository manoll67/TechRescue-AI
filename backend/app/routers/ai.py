from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..dependencies import get_current_user
from ..core.models import UserRecord

router = APIRouter(prefix="/ai", tags=["AI"])


class DiagnoseRequest(BaseModel):
    problem: str = Field(min_length=1, max_length=4000)
    operating_system: str = Field(min_length=2, max_length=50)


class DiagnoseResponse(BaseModel):
    summary: str
    steps: list[str]


@router.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(payload: DiagnoseRequest, _: UserRecord = Depends(get_current_user)) -> DiagnoseResponse:
    return DiagnoseResponse(
        summary=f"Подготвена е базова диагностика за {payload.operating_system}.",
        steps=["Провери точния текст на грешката.", "Опиши какво се е променило преди проблема.", "Не изпълнявай команди с неизвестен произход."],
    )
