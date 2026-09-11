# Retail Store Sample App

A complete retail storefront inspired by the AWS retail sample app, rebuilt from scratch as a standalone Python + FastAPI project.

## Features

- Product catalog with search and category filtering
- Shopping cart in the browser
- Checkout flow with customer details and order creation
- Order listing dashboard
- Admin page for adding, editing, and deleting products
- SQLite persistence for products and orders
- Ready-to-run FastAPI backend and simple HTML/CSS/JS frontend

## Tech stack

- Python 3.12
- FastAPI
- SQLite
- Jinja2 templates
- Vanilla JavaScript frontend

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open http://localhost:8000 in the browser.

## Admin page

Open http://localhost:8000/admin to manage products.

## Project structure

- `app/` - FastAPI application logic
- `frontend/` - templates and frontend assets
- `data/` - SQLite database files
- `tests/` - API tests

## Notes

This application is designed as a self-contained sample storefront and is intentionally lightweight so it can run locally without a large frontend build pipeline.
