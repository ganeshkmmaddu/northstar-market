from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_homepage_loads():
    response = client.get('/')
    assert response.status_code == 200
    assert 'Northstar Market' in response.text


def test_products_endpoint_returns_data():
    response = client.get('/api/products')
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) > 0
    assert 'name' in payload[0]


def test_categories_endpoint_returns_data():
    response = client.get('/api/categories')
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 5
    assert payload[0]['name'] == 'Electronics'


def test_checkout_requires_items():
    bad_request = {
        'customer_name': 'Jane Doe',
        'email': 'jane@example.com',
        'address': '123 Market St',
        'city': 'San Jose',
        'payment_method': 'Card',
        'items': [],
    }
    response = client.post('/api/orders/checkout', json=bad_request)
    assert response.status_code == 400


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'ok'
    assert payload['app'] == 'Northstar Market'


def test_stats_endpoint():
    response = client.get('/api/stats')
    assert response.status_code == 200
    payload = response.json()
    assert payload['product_count'] > 0
    assert payload['category_count'] > 0
    assert payload['order_count'] >= 0


def test_admin_login_flow():
    login_page = client.get('/admin/login')
    assert login_page.status_code == 200

    login_response = client.post('/admin/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=False)
    assert login_response.status_code == 303
    assert 'admin_session' in login_response.cookies

    protected = client.get('/admin', follow_redirects=False)
    assert protected.status_code == 200


def test_admin_api_requires_auth():
    unauthenticated_client = TestClient(app)
    response = unauthenticated_client.post('/api/admin/products', json={
        'name': 'Test unauthorized product',
        'description': 'This should be blocked',
        'price': 15.0,
        'stock': 5,
        'category_id': 1,
        'featured': False,
        'rating': 4.5,
    })
    assert response.status_code == 401


def test_product_detail_page_loads():
    response = client.get('/product/1')
    assert response.status_code == 200
    assert 'Echo Smart Speaker' in response.text


def test_order_history_endpoint_returns_empty_for_unknown_email():
    response = client.get('/api/orders/history?email=unknown@example.com')
    assert response.status_code == 200
    assert response.json() == []


def test_order_history_page_loads():
    response = client.get('/orders')
    assert response.status_code == 200
    assert 'Order history' in response.text
