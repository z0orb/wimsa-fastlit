from datetime import datetime

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    product_id: int
    quantity: int
    reference: str | None = None
    notes: str | None = None


class TransactionOut(BaseModel):
    id: int
    product_id: int
    type: str
    quantity: int
    reference: str | None
    notes: str | None
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
