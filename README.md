# Northstar Market

Northstar Market is a full-stack retail storefront designed as a polished, cloud-ready commerce sample. It combines a FastAPI backend, SQLite persistence, and a lightweight browser UI for product browsing, cart management, checkout, and inventory administration.

## Highlights

- Product catalog with search and category filters
- Interactive shopping cart and checkout workflow
- Order creation and recent-order tracking
- Admin dashboard for creating, editing, and deleting products
- SQLite-backed persistence for products, categories, and orders
- Simple deployment-friendly architecture for local or cloud-hosted environments

## Tech stack

- Python 3.12
- FastAPI
- SQLite
- Jinja2 templates
- Vanilla JavaScript frontend
- Pytest for API validation

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
4. Open http://localhost:8000 in the browser.

## Admin interface

Open http://localhost:8000/admin to manage inventory and review recent orders.

## Project structure

- `app/` - FastAPI application logic and database layer
- `frontend/` - storefront and admin templates plus static assets
- `data/` - SQLite database storage
- `tests/` - automated route and API checks

## Notes

This project is intentionally lightweight and easy to run locally. It is structured to be a strong foundation for a retail commerce demo and is ready to extend toward a cloud deployment pipeline when needed.
