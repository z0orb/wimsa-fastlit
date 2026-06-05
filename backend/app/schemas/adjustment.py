from datetime import datetime

from pydantic import BaseModel


class AdjustmentCreate(BaseModel):
    product_id: int
    new_quantity: int
    reason: str
    notes: str | None = None


class AdjustmentOut(BaseModel):
    id: int
    product_id: int
    previous_quantity: int
    new_quantity: int
    reason: str
    notes: str | None
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
