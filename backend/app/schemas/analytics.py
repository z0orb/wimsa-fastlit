from pydantic import BaseModel


class ReorderPointItem(BaseModel):
    product_id: int
    product_name: str
    sku: str
    stock_quantity: int
    min_stock_level: int
    deficit: int


class MovementTrendItem(BaseModel):
    product_id: int
    product_name: str
    sku: str
    total_inbound: int
    total_outbound: int
    net_movement: int


class WarehouseCapacity(BaseModel):
    total_capacity: int
    used_capacity: int
    utilization_pct: float
