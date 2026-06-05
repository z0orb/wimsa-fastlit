from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def get_by_sku(self, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku)
        return self.db.scalar(stmt)

    def get_below_min_stock(self) -> list[Product]:
        stmt = select(Product).where(Product.stock_quantity < Product.min_stock_level)
        return list(self.db.scalars(stmt).all())
