from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.transaction import Transaction
from app.repositories.product import ProductRepository
from app.repositories.transaction import TransactionRepository


class TransactionService:
    def __init__(self, db: Session):
        self.txn_repo = TransactionRepository(db)
        self.prod_repo = ProductRepository(db)

    def _update_stock(self, product_id: int, delta: int) -> Product:
        product = self.prod_repo.get(product_id)
        if not product:
            raise ValueError("Product not found")
        new_qty = product.stock_quantity + delta
        if new_qty < 0:
            raise ValueError("Insufficient stock")
        return self.prod_repo.update(product_id, stock_quantity=new_qty)

    def inbound(self, data: dict, user_id: int) -> Transaction:
        self._update_stock(data["product_id"], data["quantity"])
        return self.txn_repo.create(type="inbound", created_by=user_id, **data)

    def outbound(self, data: dict, user_id: int) -> Transaction:
        self._update_stock(data["product_id"], -data["quantity"])
        return self.txn_repo.create(type="outbound", created_by=user_id, **data)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Transaction]:
        return self.txn_repo.get_all(skip=skip, limit=limit)

    def get_by_id(self, id: int) -> Transaction | None:
        return self.txn_repo.get(id)
