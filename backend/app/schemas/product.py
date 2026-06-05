from datetime import datetime

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    sku: str
    category: str
    location: str
    stock_quantity: int = 0
    min_stock_level: int = 10
    max_capacity: int = 100


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    category: str | None = None
    location: str | None = None
    stock_quantity: int | None = None
    min_stock_level: int | None = None
    max_capacity: int | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    location: str
    stock_quantity: int
    min_stock_level: int
    max_capacity: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
