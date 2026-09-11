import base64
import hashlib
import hmac
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import ADMIN_PASSWORD, ADMIN_USERNAME, APP_ENV, APP_NAME, SESSION_SECRET_KEY
from app.database import (
    create_order,
    create_product,
    delete_product,
    ensure_database,
    get_categories,
    get_dashboard_stats,
    get_order_by_id,
    get_orders,
    get_product_by_id,
    get_products,
    update_order_status,
    update_product,
)
from app.schemas import CheckoutRequest, OrderStatusUpdate, ProductInput

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


def _sign_payload(payload: str) -> str:
    digest = hmac.new(SESSION_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def _create_session(username: str) -> str:
    payload = f"{username}:{int(time.time())}"
    return f"{payload}.{_sign_payload(payload)}"


def _verify_session(session_value: str | None) -> str | None:
    if not session_value:
        return None
    try:
        payload, signature = session_value.split(".", 1)
    except ValueError:
        return None
    if not hmac.compare_digest(signature, _sign_payload(payload)):
        return None
    username = payload.split(":", 1)[0]
    if username == ADMIN_USERNAME:
        return username
    return None


def _require_admin(request: Request):
    session_value = request.cookies.get("admin_session")
    username = _verify_session(session_value)
    if username != ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return username


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_database()
    yield


app = FastAPI(title=APP_NAME, version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": APP_NAME,
        "environment": APP_ENV,
        "database": "sqlite",
    }


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/product/{product_id}")
async def product_detail(request: Request, product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return templates.TemplateResponse(request, "product.html", {"product": product})


@app.get("/orders")
async def order_history_page(request: Request):
    return templates.TemplateResponse(request, "orders.html", {"orders": []})


@app.get("/order/confirmation/{order_id}")
async def order_confirmation_page(request: Request, order_id: int):
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return templates.TemplateResponse(request, "confirmation.html", {"order": order})


@app.get("/admin/login")
async def admin_login(request: Request):
    admin_session = request.cookies.get("admin_session")
    if _verify_session(admin_session) == ADMIN_USERNAME:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/admin/login")
async def admin_login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid username or password."})
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie("admin_session", _create_session(username), httponly=True, samesite="lax")
    return response


@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    return response


@app.get("/admin")
async def admin(request: Request):
    if _verify_session(request.cookies.get("admin_session")) != ADMIN_USERNAME:
        return RedirectResponse(url="/admin/login", status_code=303)
    return templates.TemplateResponse(request, "admin.html", {})


@app.get("/api/categories")
def list_categories():
    return get_categories()


@app.get("/api/products")
def list_products(category: str | None = Query(default=None), q: str | None = Query(default=None)):
    return get_products(category=category, query=q)


@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product


@app.post("/api/orders/checkout")
def checkout(payload: CheckoutRequest):
    try:
        normalized = payload.model_dump()
        if normalized.get("card_number"):
            normalized["card_last4"] = normalized["card_number"][-4:]
        return create_order(normalized)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/orders")
def list_orders():
    return get_orders()


@app.get("/api/orders/history")
def order_history(email: str | None = None):
    if not email:
        return []
    normalized_email = email.strip().lower()
    return [
        order for order in get_orders() if (order.get("email") or "").strip().lower() == normalized_email
    ]


@app.get("/api/orders/{order_id}")
def fetch_order(order_id: int):
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


@app.get("/api/stats")
def dashboard_stats():
    return get_dashboard_stats()


@app.post("/api/admin/products")
def admin_create_product(request: Request, product: ProductInput):
    _require_admin(request)
    created = create_product(product.model_dump())
    return created


@app.put("/api/admin/products/{product_id}")
def admin_update_product(request: Request, product_id: int, product: ProductInput):
    _require_admin(request)
    updated = update_product(product_id, product.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found.")
    return updated


@app.patch("/api/admin/orders/{order_id}/status")
def admin_update_order_status(request: Request, order_id: int, payload: OrderStatusUpdate):
    _require_admin(request)
    updated = update_order_status(order_id, payload.fulfillment_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found.")
    return updated


@app.delete("/api/admin/products/{product_id}")
def admin_delete_product(request: Request, product_id: int):
    _require_admin(request)
    deleted = delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found.")
    return {"success": True, "message": "Product deleted."}


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(FRONTEND_DIR / "static" / "favicon.svg")
