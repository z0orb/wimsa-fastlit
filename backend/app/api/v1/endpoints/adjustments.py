from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.adjustment import AdjustmentCreate, AdjustmentOut
from app.services.adjustment import AdjustmentService

router = APIRouter()


@router.get("", response_model=list[AdjustmentOut])
def list_adjustments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("supervisor")),
):
    svc = AdjustmentService(db)
    return svc.get_all(skip=skip, limit=limit)


@router.post("", response_model=AdjustmentOut, status_code=201)
def create_adjustment(
    data: AdjustmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("supervisor")),
):
    svc = AdjustmentService(db)
    try:
        return svc.create(data.model_dump(), user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
