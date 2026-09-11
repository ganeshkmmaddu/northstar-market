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
2. Copy the sample environment file and adjust any settings you want to override:
   ```bash
   copy .env.example .env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
5. Open http://localhost:8000 in the browser.

## Cloud-ready deployment

The app is structured for cloud hosting and reads its runtime configuration from environment variables. The container startup also honors a dynamic `PORT` value, which works cleanly with platforms such as Azure App Service, Railway, Render, or container hosts.

```bash
# Example for a hosted environment
export PORT=8080
export APP_ENV=production
export SESSION_SECRET_KEY=your-very-strong-secret
python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

## Admin interface

Open http://localhost:8000/admin to manage inventory and review recent orders.

## Project structure

- `app/` - FastAPI application logic and database layer
- `frontend/` - storefront and admin templates plus static assets
- `data/` - SQLite database storage
- `tests/` - automated route and API checks

## Admin credentials

The default admin login is:

- Username: `admin`
- Password: `admin123`

These defaults can be overridden with environment variables:

```bash
export ADMIN_USERNAME=myadmin
export ADMIN_PASSWORD=supersecurepassword
export SESSION_SECRET_KEY=your-session-secret
```

## Container deployment

You can run the app in a containerized environment using Docker Compose:

```bash
docker compose up --build
```

Then open http://localhost:8000 to access the storefront.

For cloud deployment, this setup is prepared for AWS ECS, Azure Container Apps, or a simple container host. The application exposes the health endpoint at `/health`, reads environment variables for configuration, and supports a `PORT` override so it can be dropped into hosted environments without code changes.

## Notes

This project is intentionally lightweight and easy to run locally. It is structured to be a strong foundation for a retail commerce demo and is ready to extend toward a cloud deployment pipeline when needed.
