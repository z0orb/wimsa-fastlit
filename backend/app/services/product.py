from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.adjustment import StockAdjustment
from app.models.product import Product
from app.models.transaction import Transaction
from app.repositories.product import ProductRepository


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def create(self, data: dict) -> Product:
        existing = self.repo.get_by_sku(data["sku"])
        if existing:
            raise ValueError(f"Product with SKU '{data['sku']}' already exists")
        return self.repo.create(**data)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Product]:
        return self.repo.get_all(skip=skip, limit=limit)

    def get_by_id(self, id: int) -> Product | None:
        return self.repo.get(id)

    def update(self, id: int, data: dict) -> Product | None:
        if "sku" in data and data["sku"]:
            existing = self.repo.get_by_sku(data["sku"])
            if existing and existing.id != id:
                raise ValueError(f"SKU '{data['sku']}' already in use")
        return self.repo.update(id, **data)

    def delete(self, id: int) -> bool:
        product = self.repo.get(id)
        if not product:
            return False

        txn_stmt = select(Transaction).where(Transaction.product_id == id)
        if self.repo.db.scalar(txn_stmt):
            raise ValueError("Cannot delete product with existing transactions")

        adj_stmt = select(StockAdjustment).where(StockAdjustment.product_id == id)
        if self.repo.db.scalar(adj_stmt):
            raise ValueError("Cannot delete product with existing stock adjustments")

        return self.repo.delete(id)
