import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")


class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


#Internal helpers
def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _raise_for_error(response: requests.Response) -> None:
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", "Unknown error")
        except Exception:
            detail = response.text or "Unknown error"
        raise APIError(response.status_code, detail)


def _get(path: str, token: str, params: dict = None):
    try:
        r = requests.get(
            f"{BASE_URL}{path}",
            headers=_headers(token),
            params=params,
            timeout=30,
        )
    except (requests.ConnectionError, requests.Timeout):
        raise APIError(0, "Cannot connect to backend. Is it running?")
    _raise_for_error(r)
    return r.json()


def _post(path: str, body: dict, token: str = None):
    headers = _headers(token) if token else {}
    try:
        r = requests.post(
            f"{BASE_URL}{path}",
            headers=headers,
            json=body,
            timeout=30,
        )
    except (requests.ConnectionError, requests.Timeout):
        raise APIError(0, "Cannot connect to backend. Is it running?")
    _raise_for_error(r)
    return r.json()


def _put(path: str, token: str, body: dict):
    try:
        r = requests.put(
            f"{BASE_URL}{path}",
            headers=_headers(token),
            json=body,
            timeout=30,
        )
    except (requests.ConnectionError, requests.Timeout):
        raise APIError(0, "Cannot connect to backend. Is it running?")
    _raise_for_error(r)
    return r.json()


def _delete(path: str, token: str):
    try:
        r = requests.delete(
            f"{BASE_URL}{path}",
            headers=_headers(token),
            timeout=30,
        )
    except (requests.ConnectionError, requests.Timeout):
        raise APIError(0, "Cannot connect to backend. Is it running?")
    _raise_for_error(r)


#Auth
def login(username: str, password: str) -> dict:
    """POST /auth/login → {access_token, token_type}"""
    return _post("/auth/login", body={"username": username, "password": password})


def get_me(token: str) -> dict:
    """GET /auth/me → {id, username, email, role, is_active, created_at}"""
    return _get("/auth/me", token=token)


#Products

def get_products(token: str, skip: int = 0, limit: int = 100) -> list:
    """GET /products → list[ProductOut]"""
    return _get("/products", token=token, params={"skip": skip, "limit": limit})


def create_product(token: str, payload: dict) -> dict:
    """POST /products (supervisor) → ProductOut"""
    return _post("/products", body=payload, token=token)


def update_product(token: str, product_id: int, payload: dict) -> dict:
    """PUT /products/{id} (supervisor) → ProductOut"""
    return _put(f"/products/{product_id}", token=token, body=payload)


def delete_product(token: str, product_id: int) -> None:
    """DELETE /products/{id} (supervisor) → 204"""
    _delete(f"/products/{product_id}", token=token)


#Transactions

def get_transactions(token: str, skip: int = 0, limit: int = 100) -> list:
    """GET /transactions → list[TransactionOut]"""
    return _get("/transactions", token=token, params={"skip": skip, "limit": limit})


def create_inbound(token: str, payload: dict) -> dict:
    """POST /transactions/inbound → TransactionOut"""
    return _post("/transactions/inbound", body=payload, token=token)


def create_outbound(token: str, payload: dict) -> dict:
    """POST /transactions/outbound → TransactionOut"""
    return _post("/transactions/outbound", body=payload, token=token)


#Adjustments
def get_adjustments(token: str, skip: int = 0, limit: int = 100) -> list:
    """GET /adjustments (supervisor) → list[AdjustmentOut]"""
    return _get("/adjustments", token=token, params={"skip": skip, "limit": limit})


def create_adjustment(token: str, payload: dict) -> dict:
    """POST /adjustments (supervisor) → AdjustmentOut"""
    return _post("/adjustments", body=payload, token=token)


#Analytics

def get_reorder_points(token: str) -> list:
    """GET /analytics/reorder-points (supervisor) → list[ReorderPointItem]"""
    return _get("/analytics/reorder-points", token=token)


def get_movement_trends(token: str) -> list:
    """GET /analytics/movement-trends (supervisor) → list[MovementTrendItem]"""
    return _get("/analytics/movement-trends", token=token)


def get_warehouse_capacity(token: str) -> dict:
    """GET /analytics/warehouse-capacity (supervisor) → WarehouseCapacity"""
    return _get("/analytics/warehouse-capacity", token=token)
