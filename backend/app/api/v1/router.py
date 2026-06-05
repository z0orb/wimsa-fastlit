from fastapi import APIRouter

from app.api.v1.endpoints import auth, products, transactions, adjustments, analytics

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
router.include_router(adjustments.router, prefix="/adjustments", tags=["Adjustments"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
