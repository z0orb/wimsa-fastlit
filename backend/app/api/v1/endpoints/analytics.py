from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.analytics import MovementTrendItem, ReorderPointItem, WarehouseCapacity
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/reorder-points", response_model=list[ReorderPointItem])
def reorder_points(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("supervisor")),
):
    svc = AnalyticsService(db)
    return svc.get_reorder_points()


@router.get("/movement-trends", response_model=list[MovementTrendItem])
def movement_trends(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("supervisor")),
):
    svc = AnalyticsService(db)
    return svc.get_movement_trends()


@router.get("/warehouse-capacity", response_model=WarehouseCapacity)
def warehouse_capacity(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("supervisor")),
):
    svc = AnalyticsService(db)
    return svc.get_warehouse_capacity()
