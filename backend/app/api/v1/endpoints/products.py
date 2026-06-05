from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.product import ProductService

router = APIRouter()


@router.get("", response_model=list[ProductOut])
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = ProductService(db)
    return svc.get_all(skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    svc = ProductService(db)
    product = svc.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("supervisor")),
):
    svc = ProductService(db)
    try:
        return svc.create(data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("supervisor")),
):
    svc = ProductService(db)
    try:
        product = svc.update(product_id, data.model_dump(exclude_none=True))
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("supervisor")),
):
    svc = ProductService(db)
    if not svc.delete(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
