from sqlalchemy.orm import Session

from app.models.adjustment import StockAdjustment
from app.repositories.base import BaseRepository


class AdjustmentRepository(BaseRepository[StockAdjustment]):
    def __init__(self, db: Session):
        super().__init__(StockAdjustment, db)
