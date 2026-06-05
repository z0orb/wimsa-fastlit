from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(Transaction, db)

    def get_by_type(self, type: str) -> list[Transaction]:
        stmt = select(Transaction).where(Transaction.type == type)
        return list(self.db.scalars(stmt).all())

    def get_by_product(self, product_id: int) -> list[Transaction]:
        stmt = select(Transaction).where(Transaction.product_id == product_id)
        return list(self.db.scalars(stmt).all())

    def get_movement_summary(self) -> list[tuple[int, str, int]]:
        stmt = (
            select(
                Transaction.product_id,
                Transaction.type,
                func.sum(Transaction.quantity).label("total"),
            )
            .group_by(Transaction.product_id, Transaction.type)
        )
        return list(self.db.execute(stmt).all())
