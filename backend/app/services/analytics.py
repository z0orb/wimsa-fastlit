from collections import defaultdict

from sqlalchemy.orm import Session

from app.repositories.product import ProductRepository
from app.repositories.transaction import TransactionRepository
from app.schemas.analytics import (
    MovementTrendItem,
    ReorderPointItem,
    WarehouseCapacity,
)


class AnalyticsService:
    def __init__(self, db: Session):
        self.prod_repo = ProductRepository(db)
        self.txn_repo = TransactionRepository(db)

    def get_reorder_points(self) -> list[ReorderPointItem]:
        products = self.prod_repo.get_below_min_stock()
        return [
            ReorderPointItem(
                product_id=p.id,
                product_name=p.name,
                sku=p.sku,
                stock_quantity=p.stock_quantity,
                min_stock_level=p.min_stock_level,
                deficit=p.min_stock_level - p.stock_quantity,
            )
            for p in products
        ]

    def get_movement_trends(self) -> list[MovementTrendItem]:
        products = self.prod_repo.get_all(limit=1000)
        rows = self.txn_repo.get_movement_summary()
        summary: dict[int, dict[str, int]] = defaultdict(
            lambda: {"inbound": 0, "outbound": 0}
        )
        for product_id, txn_type, total in rows:
            summary[product_id][txn_type] = total
        prod_map = {p.id: p for p in products}
        result = []
        for pid, vals in summary.items():
            p = prod_map.get(pid)
            if not p:
                continue
            result.append(
                MovementTrendItem(
                    product_id=pid,
                    product_name=p.name,
                    sku=p.sku,
                    total_inbound=vals["inbound"],
                    total_outbound=vals["outbound"],
                    net_movement=vals["inbound"] - vals["outbound"],
                )
            )
        return result

    def get_warehouse_capacity(self) -> WarehouseCapacity:
        products = self.prod_repo.get_all(limit=1000)
        total_capacity = sum(p.max_capacity for p in products) or 1
        used_capacity = sum(p.stock_quantity for p in products)
        return WarehouseCapacity(
            total_capacity=total_capacity,
            used_capacity=used_capacity,
            utilization_pct=round((used_capacity / total_capacity) * 100, 2),
        )
