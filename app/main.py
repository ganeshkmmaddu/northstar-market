from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import APP_ENV, APP_NAME
from app.database import (
    create_order,
    create_product,
    delete_product,
    ensure_database,
    get_categories,
    get_dashboard_stats,
    get_orders,
    get_product_by_id,
    get_products,
    update_product,
)
from app.schemas import CheckoutRequest, ProductInput

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


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


@app.get("/admin")
async def admin(request: Request):
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
        return create_order(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/orders")
def list_orders():
    return get_orders()


@app.get("/api/stats")
def dashboard_stats():
    return get_dashboard_stats()


@app.post("/api/admin/products")
def admin_create_product(product: ProductInput):
    created = create_product(product.model_dump())
    return created


@app.put("/api/admin/products/{product_id}")
def admin_update_product(product_id: int, product: ProductInput):
    updated = update_product(product_id, product.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found.")
    return updated


@app.delete("/api/admin/products/{product_id}")
def admin_delete_product(product_id: int):
    deleted = delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found.")
    return {"success": True, "message": "Product deleted."}


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(FRONTEND_DIR / "static" / "favicon.svg")
