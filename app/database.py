import sqlite3

from app.config import DATABASE_PATH

DB_PATH = DATABASE_PATH

DEFAULT_CATEGORIES = [
    (1, "Electronics", "Smart devices and everyday tech"),
    (2, "Fashion", "Style upgrades for work and weekends"),
    (3, "Home & Living", "Comfort products for home life"),
    (4, "Sports", "Fitness and activity essentials"),
    (5, "Beauty", "Self-care and wellness products"),
]

DEFAULT_PRODUCTS = [
    (1, "Echo Smart Speaker", "Voice-controlled speaker with room-filling sound and smart home controls.", 89.99, 28, 1, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80", 1, 4.7),
    (2, "AirFlow Pro Headphones", "Wireless headphones with deep bass and all-day comfort.", 129.99, 26, 1, "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80", 1, 4.8),
    (3, "Summit Backpack", "Weather-ready day pack with laptop sleeve and hydration pocket.", 64.5, 18, 2, "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80", 1, 4.5),
    (4, "Luna Knit Sweater", "Soft knit layer with a tailored silhouette for cooler days.", 54.0, 31, 2, "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80", 0, 4.6),
    (5, "Harbor Table Lamp", "Minimalist lamp with warm ambient lighting for any room.", 42.75, 22, 3, "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80", 1, 4.4),
    (6, "Trail Runner Shoes", "Lightweight running shoes built for comfort and traction.", 94.5, 20, 4, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80", 1, 4.7),
    (7, "Glow Serum", "Vitamin-rich facial serum to keep skin hydrated and radiant.", 32.0, 45, 5, "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=900&q=80", 0, 4.5),
    (8, "Crest Coffee Maker", "Compact coffee maker designed for busy mornings and quick brews.", 72.25, 17, 3, "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=80", 1, 4.6),
]


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                image_url TEXT,
                featured INTEGER DEFAULT 0,
                rating REAL DEFAULT 4.5,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT,
                payment_method TEXT NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'confirmed',
                payment_status TEXT DEFAULT 'paid',
                card_last4 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS product_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS loyalty_accounts (
                email TEXT PRIMARY KEY,
                points INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        order_columns = [
            row[1] for row in conn.execute("PRAGMA table_info(orders)").fetchall()
        ]
        if "status" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'confirmed'")
        if "payment_status" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'paid'")
        if "card_last4" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN card_last4 TEXT")
        if "fulfillment_status" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN fulfillment_status TEXT DEFAULT 'processing'")
        if "tracking_number" not in order_columns:
            conn.execute("ALTER TABLE orders ADD COLUMN tracking_number TEXT")

        if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO categories (id, name, description) VALUES (?, ?, ?)",
                DEFAULT_CATEGORIES,
            )

        if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO products (id, name, description, price, stock, category_id, image_url, featured, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                DEFAULT_PRODUCTS,
            )


def get_categories():
    ensure_database()
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
        return [dict(row) for row in rows]


def get_products(category: str | None = None, query: str | None = None):
    ensure_database()
    base_sql = """
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON c.id = p.category_id
    """
    clauses = []
    params = []

    if category:
        clauses.append("c.name = ?")
        params.append(category)

    if query:
        needle = f"%{query.lower()}%"
        clauses.append("(LOWER(p.name) LIKE ? OR LOWER(p.description) LIKE ?)")
        params.extend([needle, needle])

    if clauses:
        base_sql += " WHERE " + " AND ".join(clauses)

    base_sql += " ORDER BY p.featured DESC, p.id ASC"

    with get_connection() as conn:
        rows = conn.execute(base_sql, params).fetchall()
        return [dict(row) for row in rows]


def get_product_by_id(product_id: int):
    ensure_database()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT p.*, c.name AS category_name
            FROM products p
            JOIN categories c ON c.id = p.category_id
            WHERE p.id = ?
            """,
            (product_id,),
        ).fetchone()
        return dict(row) if row else None


def get_product_reviews(product_id: int):
    ensure_database()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM product_reviews
            WHERE product_id = ?
            ORDER BY created_at DESC
            """,
            (product_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def create_product_review(product_id: int, review_data: dict):
    ensure_database()
    rating = int(review_data.get("rating", 0))
    if rating < 1 or rating > 5:
        raise ValueError("Rating must be between 1 and 5.")
    customer_name = (review_data.get("customer_name") or "Customer").strip() or "Customer"
    comment = (review_data.get("comment") or "").strip()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO product_reviews (product_id, customer_name, rating, comment)
            VALUES (?, ?, ?, ?)
            """,
            (product_id, customer_name, rating, comment),
        )
        review_id = cursor.lastrowid
        review = conn.execute("SELECT * FROM product_reviews WHERE id = ?", (review_id,)).fetchone()
        return dict(review)


def get_customer_loyalty(email: str | None):
    ensure_database()
    if not email:
        return {"email": "", "points": 0}
    normalized = email.strip().lower()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT email, points FROM loyalty_accounts WHERE email = ?",
            (normalized,),
        ).fetchone()
        if row:
            return {"email": row["email"], "points": row["points"]}
        return {"email": normalized, "points": 0}


def award_loyalty_points(email: str, points: int):
    ensure_database()
    normalized = (email or "").strip().lower()
    if not normalized:
        return {"email": "", "points": 0}
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT points FROM loyalty_accounts WHERE email = ?",
            (normalized,),
        ).fetchone()
        current_points = int(existing["points"]) if existing else 0
        total_points = current_points + int(points)
        conn.execute(
            """
            INSERT INTO loyalty_accounts (email, points, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(email) DO UPDATE SET points = excluded.points, updated_at = CURRENT_TIMESTAMP
            """,
            (normalized, total_points),
        )
        return {"email": normalized, "points": total_points}


def create_product(product_data: dict):
    ensure_database()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO products (name, description, price, stock, category_id, image_url, featured, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_data["name"],
                product_data["description"],
                product_data["price"],
                product_data["stock"],
                product_data["category_id"],
                product_data.get("image_url"),
                int(bool(product_data.get("featured", False))),
                product_data.get("rating", 4.5),
            ),
        )
        product_id = cursor.lastrowid
        return get_product_by_id(product_id)


def update_product(product_id: int, product_data: dict):
    ensure_database()
    with get_connection() as conn:
        rowcount = conn.execute(
            """
            UPDATE products
            SET name = ?, description = ?, price = ?, stock = ?, category_id = ?, image_url = ?, featured = ?, rating = ?
            WHERE id = ?
            """,
            (
                product_data["name"],
                product_data["description"],
                product_data["price"],
                product_data["stock"],
                product_data["category_id"],
                product_data.get("image_url"),
                int(bool(product_data.get("featured", False))),
                product_data.get("rating", 4.5),
                product_id,
            ),
        ).rowcount
        if rowcount == 0:
            return None
        return get_product_by_id(product_id)


def delete_product(product_id: int):
    ensure_database()
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return cursor.rowcount > 0


def create_order(order_data: dict):
    ensure_database()
    items = order_data.get("items", [])
    if not items:
        raise ValueError("Checkout requires at least one item.")

    total_amount = 0.0
    payment_method = order_data.get("payment_method", "Card")
    card_last4 = (order_data.get("card_last4") or "")
    if card_last4 and len(card_last4) > 4:
        card_last4 = card_last4[-4:]
    payment_status = "paid" if payment_method.lower() not in {"cash on delivery", "cod"} else "pending"
    order_status = "confirmed" if payment_status == "paid" else "pending"
    fulfillment_status = "processing"

    with get_connection() as conn:
        for item in items:
            product = conn.execute(
                "SELECT * FROM products WHERE id = ?",
                (item["product_id"],),
            ).fetchone()
            if not product:
                raise ValueError(f"Product {item['product_id']} was not found.")
            if product["stock"] < item["quantity"]:
                raise ValueError(f"Not enough stock for product {product['name']}.")
            total_amount += float(product["price"]) * int(item["quantity"])

        order_cursor = conn.execute(
            """
            INSERT INTO orders (customer_name, email, address, city, payment_method, total_amount, status, payment_status, card_last4, fulfillment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_data["customer_name"],
                order_data["email"],
                order_data["address"],
                order_data.get("city", ""),
                payment_method,
                round(total_amount, 2),
                order_status,
                payment_status,
                card_last4 or None,
                fulfillment_status,
            ),
        )
        order_id = order_cursor.lastrowid

        for item in items:
            product = conn.execute(
                "SELECT * FROM products WHERE id = ?",
                (item["product_id"],),
            ).fetchone()
            quantity = int(item["quantity"])
            unit_price = float(product["price"])
            line_total = unit_price * quantity
            conn.execute(
                """
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, product["id"], quantity, unit_price, line_total),
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (quantity, product["id"]),
            )

        customer_email = (order_data.get("email") or "").strip().lower()
        if customer_email:
            reward_points = max(1, int(round(total_amount * 2)))
            existing = conn.execute(
                "SELECT points FROM loyalty_accounts WHERE email = ?",
                (customer_email,),
            ).fetchone()
            current_points = int(existing["points"]) if existing else 0
            total_points = current_points + reward_points
            conn.execute(
                """
                INSERT INTO loyalty_accounts (email, points, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(email) DO UPDATE SET points = excluded.points, updated_at = CURRENT_TIMESTAMP
                """,
                (customer_email, total_points),
            )

        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        order_items = conn.execute(
            """
            SELECT oi.*, p.name AS product_name
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = ?
            """,
            (order_id,),
        ).fetchall()

        result = dict(order)
        result["items"] = [dict(row) for row in order_items]
        return result


def get_order_by_id(order_id: int):
    ensure_database()
    with get_connection() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not order:
            return None
        items = conn.execute(
            """
            SELECT oi.*, p.name AS product_name, p.image_url
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = ?
            """,
            (order_id,),
        ).fetchall()
        payload = dict(order)
        payload["items"] = [dict(item) for item in items]
        return payload


def get_orders():
    ensure_database()
    with get_connection() as conn:
        orders = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
        results = []
        for order in orders:
            items = conn.execute(
                """
                SELECT oi.*, p.name AS product_name, p.image_url
                FROM order_items oi
                JOIN products p ON p.id = oi.product_id
                WHERE oi.order_id = ?
                """,
                (order["id"],),
            ).fetchall()
            payload = dict(order)
            payload["items"] = [dict(item) for item in items]
            results.append(payload)
        return results


def update_order_status(order_id: int, fulfillment_status: str):
    ensure_database()
    allowed = {"processing", "packed", "shipped", "delivered"}
    value = (fulfillment_status or "processing").strip().lower()
    if value not in allowed:
        raise ValueError("Invalid fulfillment status.")

    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE orders SET fulfillment_status = ? WHERE id = ?",
            (value, order_id),
        )
        if cursor.rowcount == 0:
            return None
        conn.commit()
        updated = get_order_by_id(order_id)
        return updated


def get_dashboard_stats():
    ensure_database()
    with get_connection() as conn:
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        revenue = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders").fetchone()[0]
        low_stock = conn.execute("SELECT COUNT(*) FROM products WHERE stock < 10").fetchone()[0]

        return {
            "product_count": product_count,
            "category_count": category_count,
            "order_count": order_count,
            "revenue": round(float(revenue or 0), 2),
            "low_stock_alerts": low_stock,
        }
