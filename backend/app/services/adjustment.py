from sqlalchemy.orm import Session

from app.models.adjustment import StockAdjustment
from app.models.product import Product
from app.repositories.adjustment import AdjustmentRepository
from app.repositories.product import ProductRepository


class AdjustmentService:
    def __init__(self, db: Session):
        self.adj_repo = AdjustmentRepository(db)
        self.prod_repo = ProductRepository(db)

    def create(self, data: dict, user_id: int) -> StockAdjustment:
        product = self.prod_repo.get(data["product_id"])
        if not product:
            raise ValueError("Product not found")
        previous = product.stock_quantity
        new_qty = data["new_quantity"]
        self.prod_repo.update(data["product_id"], stock_quantity=new_qty)
        return self.adj_repo.create(
            product_id=data["product_id"],
            previous_quantity=previous,
            new_quantity=new_qty,
            reason=data["reason"],
            notes=data.get("notes"),
            created_by=user_id,
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[StockAdjustment]:
        return self.adj_repo.get_all(skip=skip, limit=limit)
