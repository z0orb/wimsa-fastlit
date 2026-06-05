from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.services.transaction import TransactionService

router = APIRouter()


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TransactionService(db)
    return svc.get_all(skip=skip, limit=limit)


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TransactionService(db)
    txn = svc.get_by_id(transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.post("/inbound", response_model=TransactionOut, status_code=201)
def inbound(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TransactionService(db)
    try:
        return svc.inbound(data.model_dump(), user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/outbound", response_model=TransactionOut, status_code=201)
def outbound(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = TransactionService(db)
    try:
        return svc.outbound(data.model_dump(), user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
